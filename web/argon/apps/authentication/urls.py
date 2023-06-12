# -*- encoding: utf-8 -*-

from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('test/', views.recipe_detail_view, name='recipe'),
    path('recipe/<str:cuisine>/', views.recipe_detail_view, name='recipe_by_cuisine')
]

