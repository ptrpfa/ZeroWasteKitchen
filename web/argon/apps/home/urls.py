# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),                                             # The home page
    path('recipe/', views.recipe_view, name='recipe'),
    path('recipe/<str:cuisine>/', views.recipe_view, name='recipe_by_cuisine'),
    path('recipe_details/', views.recipe_details, name='recipe_details'),
    re_path(r'^.*\.*', views.pages, name='pages')                                 # Matches any html file
]
