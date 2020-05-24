from urllib.parse import urlencode

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .engine import *

# Create your views here.
from questions.models import Question


def index(request):
    # FIXME: replace user
    context = {'stats': calculate_stats(None)}

    return render(request, 'questions/index.html', context)


def ask(request):
    # FIXME: replace user
    stats = calculate_stats(None)
    categories = slowest_progress(stats)
    # FIXME: replace user
    questions = get_preferred_questions(categories, None)
    if len(questions) == 0:
        return render(request, 'questions/congrats.html')
    question = get_random_question(questions)
    print(question.media)
    return render(request, 'questions/ask.html', {'question': question})


def check(request):
    question = get_object_or_404(Question, pk=request.POST['question_id'])
    active_answers = question.answers.filter(inactive=False)
    proper_answers = set(answer.id for answer in active_answers.filter(is_correct=True))
    print(request.POST)
    picked = set(map(int, request.POST.getlist('picked')))
    is_correct = False
    context = {'question': question,
               'error': None}

    if not picked:
        context['error'] = 'Musisz wybrać co najmniej jedną odpowiedź!'
        return render(request, 'questions/ask.html', context)
    if active_answers.count() == len(picked):
        context['error'] = 'Co najmniej jedna odpowiedź musi zostać pusta!'
        return render(request, 'questions/ask.html', context)
    context['picked'] = picked
    if picked == proper_answers:
        context['message'] = 'Poprawna odpowiedź!'
        context['message_type'] = 'success'
        is_correct = True
    else:
        context['message'] = 'Błędna odpowiedź.'
        context['message_type'] = 'danger'

    # FIXME: replace user
    log_answer(None, question, picked, is_correct)

    return render(request, 'questions/check.html', context)
