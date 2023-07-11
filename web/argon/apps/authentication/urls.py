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
    path('remove_image/<int:review_id>/', views.remove_image, name='remove_image'),
    path('profile.html', views.view_profile, name='view_profile'),
    path('update_restriction/', views.update_restriction, name='update_restriction'),
]

