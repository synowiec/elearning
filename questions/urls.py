from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check, name='check'),
    path('ask/', views.ask, name='ask')
]