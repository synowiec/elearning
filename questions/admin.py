from django.contrib import admin
from django.utils.safestring import mark_safe

from questions.forms import SubcategoryFormSet, AnswerFormSet
from questions.models import Category, Subcategory, Question, Answer


class Answers(admin.TabularInline):
    model = Answer
    readonly_fields = ('created_by', 'created_at')
    formset = AnswerFormSet

    def has_delete_permission(self, request, obj=None):
        return False


class Questions(admin.ModelAdmin):
    inlines = [Answers]
    list_display = ('_text', 'answers_display', 'subcategory_display', 'created_by', 'created_at', 'inactive')
    search_fields = ('text', 'answers__text')
    readonly_fields = ('created_by', 'created_at')
    filter_horizontal = ('subcategory',)
    list_filter = ('subcategory', 'inactive','created_by', 'created_at')

    @mark_safe
    def answers_display(self, obj):
        return '<br>'.join([
            ('<b>' if child.is_correct else '') +
            ('<del>' if child.inactive else '') +
            chr(i) + '. ' + child.text +
            ('</del>' if child.inactive else '') +
            ('</b>' if child.is_correct else '')
            for i, child in enumerate(obj.answers.all(), start=65)])

    answers_display.short_description = 'Answers'

    @mark_safe
    def subcategory_display(self, obj):
        return '<br>'.join([child.category.text + ' | ' + child.text for child in obj.subcategory.all()])

    subcategory_display.short_description = 'Subcategories'

    def _text(self, obj):
        return obj.text

    _text.short_description = 'Question'

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()


class Subcategories(admin.TabularInline):
    model = Subcategory
    readonly_fields = ('created_by', 'created_at')
    formset = SubcategoryFormSet

    def has_delete_permission(self, request, obj=None):
        return False


class Categories(admin.ModelAdmin):
    inlines = [Subcategories]
    list_display = ('_text', 'subcategory_display', 'created_by', 'created_at', 'inactive')
    readonly_fields = ('created_by', 'created_at')
    search_fields = ('text', 'category_subcategory__text')
    list_filter = ('created_by', 'created_at')

    @mark_safe
    def subcategory_display(self, obj):
        return ", ".join([
            ('<del>' + child.text + '</del>' if child.inactive else child.text)
            for child in obj.category_subcategory.all()])

    subcategory_display.short_description = 'Subcategories'

    def _text(self, obj):
        return obj.text

    _text.short_description = 'Category'

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()


admin.site.register(Question, Questions)
admin.site.register(Category, Categories)
