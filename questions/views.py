from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from .decorators import unauthenticated_user
from .engine import *
from .forms import RegisterForm


class RegisterPage(View):
    form = RegisterForm()
    context = {'form': form}

    @unauthenticated_user
    def get(self, request):
        return render(request, 'dashboard/register.html', self.context)

    @unauthenticated_user
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Konto ' + username + ' zostało utworzone.')
            return redirect('dashboard/login')

        self.context = {'form': form}
        return render(request, 'dashboard/register.html', self.context)


class LoginPage(View):
    context = {}

    @unauthenticated_user
    def get(self, request):
        return render(request, 'dashboard/login.html', self.context)

    @unauthenticated_user
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('questions:index')
        else:
            messages.info(request, 'Użytkownik lub hasło jest nieprawidłowe')
        return render(request, 'dashboard/login.html', self.context)


@login_required(login_url='questions:login')
def log_out(request):
    logout(request)
    return redirect('questions:login')


@login_required(login_url='questions:login')
def index(request):
    context = {'stats': calculate_stats(request.user)}

    return render(request, 'questions/index.html', context)


@login_required(login_url='questions:login')
def ask(request):
    user = request.user
    stats = calculate_stats(user)
    categories = slowest_progress(stats)
    questions = get_preferred_questions(categories, user)
    if not questions:
        return render(request, 'questions/congrats.html')
    question = get_random_question(questions)
    return render(request, 'questions/ask.html', {'question': question})


@login_required(login_url='questions:login')
def check(request):
    question = get_object_or_404(Question, pk=request.POST['question_id'])
    active_answers = question.answers.filter(inactive=False)
    proper_answers = set(answer.id for answer in active_answers.filter(is_correct=True))
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

    log_answer(request.user, question, picked, is_correct)

    return render(request, 'questions/check.html', context)
