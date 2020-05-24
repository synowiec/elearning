from pprint import pprint

from .models import AnswerHistory, Answer, Question
from django.db.models import Max, Q, Count
from itertools import combinations
from random import choice


def get_active_questions():
    return Question.objects.filter(inactive=False)


def get_latest_proper_answered_question(user):
    # TODO user handling
    return AnswerHistory.objects.filter(Q(question__inactive=False)
                                      # & Q(user=user)
                                      )


def get_active_categories():
    stats = {}
    for q in get_active_questions():
        for sc in q.subcategory.filter(inactive=False):
            subcategory = sc.text
            category = sc.category.text
            stats.setdefault(category, {}).setdefault(subcategory, {
                'no_of_questions': 0,
                'no_of_answers': 0,
                'score': 0,
                'progress': 0
            })
            stats[category][subcategory]['no_of_questions'] += 1
    return stats


def calculate_stats(user):
    stats = get_active_categories()
    ah = get_latest_proper_answered_question(user)
    tries = ah.values('question__subcategory__category__text',
                      'question__subcategory__text').annotate(total=Count('id'))
    latest = ah.values('question__id').annotate(id=Max('id'))
    correct = ah.filter(Q(pk__in=list(a['id'] for a in latest))
                        & Q(is_correct=True)
                        ).values('question__subcategory__category__text',
                                 'question__subcategory__text').annotate(total=Count('id'))
    for t in tries:
        category = t['question__subcategory__category__text']
        subcategory = t['question__subcategory__text']
        stats[category][subcategory]['no_of_answers'] = t['total']
        total = correct.filter(Q(question__subcategory__category__text=category)
                               & Q(question__subcategory__text=subcategory)
                               )
        if len(total) > 0:
            stats[category][subcategory]['score'] = total[0]['total']
        stats[category][subcategory]['progress'] = round(
            stats[category][subcategory]['score'] / stats[category][subcategory]['no_of_questions'] * 100, 2)
    return stats


def slowest_progress(stats):
    categories = []
    progress = 100
    for category in stats:
        for subcategory in stats[category]:
            sp = stats[category][subcategory]['progress']
            if sp == 100:
                break
            elif sp < progress:
                progress = sp
                categories.clear()
                categories.append((category, subcategory))
            elif sp == progress:
                categories.append((category, subcategory))
    return categories


def get_preferred_questions(categories, user):
    set_of_queries = []
    ah = get_latest_proper_answered_question(user)
    latest = ah.values('question__id').annotate(id=Max('id'))
    correct = ah.filter(Q(pk__in=list(a['id'] for a in latest))
                        & Q(is_correct=True)
                        ).values()
    base = get_active_questions().exclude(pk__in=list(c['question_id'] for c in correct))
    size = len(categories)
    for category, subcategory in categories:
        set_of_queries.append(Q(subcategory__category__text=category) & Q(subcategory__text=subcategory))
    for r in range(size, 0, -1):
        qs = Question.objects.none()
        comb = list(combinations(set_of_queries, r))
        for c in comb:
            q = base
            for o in c:
                q = q.filter(o)
            qs |= q
        if len(qs) > 0:
            return qs


def get_random_question(questions):
    return choice(questions)


def log_answer(user, question, answers, is_correct):
    match_answers = Answer.objects.filter(pk__in=answers)
    answer = AnswerHistory.objects.create(created_by=user,
                                          question=question,
                                          is_correct=is_correct)
    for a in match_answers:
        answer.selected_answers.add(a)
    answer.save()
