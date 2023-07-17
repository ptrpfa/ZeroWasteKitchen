# -*- encoding: utf-8 -*-

from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', login_view, name="login"),                                          # Login page
    path('register/', register_user, name="register"),                                 # Register a new user
    path("logout/", LogoutView.as_view(), name="logout"),                              # Logout of user account
    path('profile/update/', views.update_profile, name='update_profile'),              # Update user profile information
    path('update_review/<int:review_id>/', views.update_review, name='update_review'), # Updates review from database
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'), # Deletes review from database
    path('get_file_data/', views.get_file_data, name='get_file_data'),                 # Retrieve file data from user reviews 
    path('remove_image/<int:review_id>/', views.remove_image, name='remove_image'),    # Delete image from review and database
    path('profile.html', views.view_profile, name='view_profile'),                     # View profile page 
    path('challenges.html', views.view_challenges, name='view_challenges'),            # View challenges page
    path('update_restriction/', views.update_restriction, name='update_restriction'),  # Update user restriction
]