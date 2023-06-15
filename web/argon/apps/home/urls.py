# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),                                             # The home page
    path(r'recipe/<int:id>/', views.view_recipe, name='view_recipe'),               # View each individual recipe
    path(r'recipe/', views.get_recipes, name='recipe'),                             # Temporary: view all recipes
    path(r'search/', views.search_recipes, name='search_recipes'),                  # Search page for recipes
    path(r'process_search/', views.process_search, name='search_recipes'),          # Server processing for recipe searches
    re_path (r'^.*\.html', views.pages, name='pages')                               # Matches any html file
]