# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),                                             # The home page
    path(r'recipe/<str:cuisine>/', views.get_recipes, name='recipe_by_cuisine'),
    path(r'recipe/', views.get_recipes, name='recipe'),
    path(r'recipe_details/', views.recipe_details, name='recipe_details'),
    path(r'test/', views.get_recipes, name='test'),
    path('recipe/details/', views.view_recipe, name='view_recipe'),
    path('recipe/details/<int:RecipeID>/', views.view_recipe, name='view_recipe'),
    re_path(r'^.*\.*', views.pages, name='pages')                                 # Matches any html file
]



