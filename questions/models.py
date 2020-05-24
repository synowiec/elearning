from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    text = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    inactive = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Subcategory(models.Model):
    text = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    inactive = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name='category_subcategory', on_delete=models.CASCADE)

    def __str__(self):
        return self.category.text + ' | ' + self.text

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'


class Question(models.Model):
    text = models.TextField()
    explanation = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    inactive = models.BooleanField(default=False)
    subcategory = models.ManyToManyField(Subcategory)

    def validate_file_type(value):
        if hasattr(value.file, 'content_type'):
            if value.file.content_type not in ('image/png', 'image/bmp', 'image/jpeg', 'image/gif',
                                               'video/mpeg', 'video/mp4', 'video/quicktime'):
                raise ValidationError(u'Wrong type of file. Accepted extensions: png, bmp, jpeg, gif, mpeg, mp4, qt')

    def validate_file_size(value):
        if value.size > 10485760:
            raise ValidationError(u'Size can\'t exceed 10 MB')

    media = models.FileField(upload_to='question_files',
                             validators=[validate_file_type, validate_file_size],
                             null=True,
                             blank=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    inactive = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class AnswerHistory(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_correct = models.BooleanField()
    question = models.ForeignKey(Question, related_name='historical_question', on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer)
