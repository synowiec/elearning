from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from questions.engine import *
from questions.models import Question, Subcategory, Category, AnswerHistory


class BaseFunctionalitiesTestCase(TestCase):
    def setUp(self):
        AnswerHistory.objects.none()
        User.objects.create(username='testuser')
        cat1 = Category.objects.create(text='cat1')
        subcat1 = Subcategory.objects.create(text='subcat1', category=cat1)
        subcat2 = Subcategory.objects.create(text='subcat2', category=cat1)
        subcat3 = Subcategory.objects.create(text='subcat3', category=cat1)
        subcat4 = Subcategory.objects.create(text='subcat4', category=cat1)
        Question.objects.create(text='q1').subcategory.add(subcat1)
        Question.objects.create(text='q2').subcategory.add(subcat2)
        Question.objects.create(text='q3').subcategory.add(subcat3)
        Question.objects.create(text='q4').subcategory.add(subcat4)

    def test_user_creation(self):
        self.assertEqual(User.objects.get(username='testuser').username, 'testuser')

    def test_user_adding_categories(self):
        self.assertEqual(Subcategory.objects.count(), 4)

    def test_adding_questions(self):
        self.assertEqual(Question.objects.count(), 4)

    def test_get_active_questions(self):
        q = Question.objects.get(text='q4')
        q.inactive = True
        q.save()
        self.assertEqual(get_active_questions().count(), 3)

    def test_get_latest_proper_answered_question(self):
        user = User.objects.get(username='testuser')
        ah = get_latest_proper_answered_question(user)
        q = Question.objects.get(text='q4')
        q.created_by = user
        q.inactive = True
        q.save()
        self.assertEqual(len(ah), 0)
        AnswerHistory.objects.create(created_by=user, is_correct=True, question=q)
        ah = get_latest_proper_answered_question(user)
        self.assertEqual(len(ah), 0)
        q.inactive = False
        q.save()
        ah = get_latest_proper_answered_question(user)
        self.assertEqual(len(ah), 1)


class EngineTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='testuser')
        cat1 = Category.objects.create(text='cat1')
        subcat1 = Subcategory.objects.create(text='subcat1', category=cat1)
        subcat2 = Subcategory.objects.create(text='subcat2', category=cat1)
        subcat3 = Subcategory.objects.create(text='subcat3', category=cat1)
        subcat4 = Subcategory.objects.create(text='subcat4', category=cat1)
        Question.objects.create(text='q1').subcategory.add(subcat1)
        Question.objects.create(text='q2').subcategory.add(subcat2)
        Question.objects.create(text='q3').subcategory.add(subcat3)
        Question.objects.create(text='q4').subcategory.add(subcat4)

    def test_get_preferred_questions_single_category(self):
        user = User.objects.get(username='testuser')
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 4)

    def test_get_preferred_questions_multiple_category(self):
        user = User.objects.get(username='testuser')
        q = Question.objects.get(text='q4')
        sc = Subcategory.objects.get(text='subcat3')
        q.subcategory.add(sc)
        q.save()
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 1)

    def test_get_preferred_questions_single_category_answer_single_category(self):
        user = User.objects.get(username='testuser')
        q = Question.objects.get(text='q4')
        AnswerHistory.objects.create(created_by=user, is_correct=True, question=q)
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 3)

    def test_get_preferred_questions_multiple_category_answer_multiple_category(self):
        user = User.objects.get(username='testuser')
        q = Question.objects.get(text='q4')
        sc = Subcategory.objects.get(text='subcat3')
        q.subcategory.add(sc)
        q.save()
        AnswerHistory.objects.create(created_by=user, question=q, is_correct=True)
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 2)

    def test_get_preferred_questions_multiple_category_answer_single_category(self):
        user = User.objects.get(username='testuser')
        q = Question.objects.get(text='q4')
        sc = Subcategory.objects.get(text='subcat3')
        q.subcategory.add(sc)
        q.save()
        q = Question.objects.get(text='q2')
        AnswerHistory.objects.create(created_by=user, question=q, is_correct=True)
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 1)

    def test_get_preferred_questions_single_category_answer_multiple_category(self):
        user = User.objects.get(username='testuser')
        q = Question.objects.get(text='q4')
        sc = Subcategory.objects.get(text='subcat3')
        q.subcategory.add(sc)
        q.save()
        AnswerHistory.objects.create(created_by=user, question=q, is_correct=True)
        stats = calculate_stats(user)
        categories = slowest_progress(stats)
        qs = get_preferred_questions(categories, user)
        self.assertEqual(len(qs), 2)
