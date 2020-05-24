from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet
from django import forms


class SubcategoryFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(SubcategoryFormSet, self)._construct_form(i, **kwargs)
        if i < 1:
            form.empty_permitted = False
        return form


class AnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super(AnswerFormSet, self).clean()
        if any(self.errors):
            return
        counter = 0
        correct = 0
        inactive = 0

        for form in self.forms:
            if form.cleaned_data.get('text') is not None:
                counter += 1
                if form.cleaned_data.get('inactive'):
                    inactive += 1
                elif form.cleaned_data.get('is_correct'):
                    correct += 1

        if counter < 2:
            raise forms.ValidationError('At least two answers needed.')
        elif counter - inactive < 2:
            raise forms.ValidationError('At least two active answers needed.')
        elif counter - inactive == correct:
            raise forms.ValidationError('At least one invalid answer needed.')
        elif correct < 1:
            raise forms.ValidationError('At least one correct answer needed.')


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
