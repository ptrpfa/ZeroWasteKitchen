# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),                                             # The home page
    path(r'recipe/<str:cuisine>/', views.recipe_view, name='recipe_by_cuisine'),
    path(r'recipe/', views.recipe_view, name='recipe'),
    path(r'recipe_details/', views.recipe_details, name='recipe_details'),
    path(r'test/', views.get_recipes, name='test'),
    re_path(r'^.*\.*', views.pages, name='pages')                                 # Matches any html file
]
