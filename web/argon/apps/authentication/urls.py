# -*- encoding: utf-8 -*-

from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('update_review/<int:review_id>/', views.update_review, name='update_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('profile.html', views.view_profile, name='view_profile'),



]

