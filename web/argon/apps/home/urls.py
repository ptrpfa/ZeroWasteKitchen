# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.search_recipes, name='home'),                                                                # Root url
    path(r'recipe/<int:id>/', views.view_recipe, name='view_recipe'),                                           # View each individual recipe
    path(r'recipe/<int:recipe_id>/', views.view_recipe, name='view_recipe'),                                    # View each individual recipe
    # path(r'recipe/', views.get_recipes, name='recipe'),                                                       # TEMPORARY: view all recipes
    path(r'search/', views.search_recipes, name='search_recipes'),                                              # Search page for recipes
    path(r'process_search/', views.process_search, name='process_search'),                                      # Server processing for recipe searches
    path(r'recipe/<int:recipe_id>/add_review/', views.add_review, name='add_review'),                           # Insert review to database
    path(r'get_suggested_ingredients/', views.get_suggested_ingredients, name='get_suggested_ingredients'),     # Server processing for getting random ingredients
    path('recipe/<int:recipe_id>/add_to_user_recipe/', views.add_to_user_recipe, name='add_to_user_recipe'),    # Insert into mapping table userrecipe
    path('recipe/<int:recipe_id>/', views.get_recipes, name='recipe'),                                          # TEMPORARY: To remove along with view
    re_path (r'^.*\.html', views.pages, name='pages')                                                           # Matches any html file
]