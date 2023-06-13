# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Recipe(models.Model):
    RecipeID = models.AutoField(primary_key=True)
    MealType = models.CharField(max_length=255)
    Cuisine = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    Description = models.CharField(max_length=255)

    class Meta:
        db_table = 'recipe'

