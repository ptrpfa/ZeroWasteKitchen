# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),                                             # The home page
    path(r'recipe/<int:id>/', views.view_recipe, name='view_recipe'),
    path(r'recipe/', views.get_recipes, name='recipe'),
    path(r'search/', views.search_recipes, name='search_recipes'),
    re_path (r'^.*\.html', views.pages, name='pages')                               # Matches any html file
]