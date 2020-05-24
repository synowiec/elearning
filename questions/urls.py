from django.urls import path

from . import views

app_name = 'questions'
urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check, name='check'),
    path('ask/', views.ask, name='ask'),
    path('register/', views.RegisterPage.as_view(), name='register'),
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.log_out, name='logout')
]