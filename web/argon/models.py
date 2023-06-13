from django.db import models

# Base models
class User(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', unique=True, max_length=100)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=100)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=100)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=100)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=100)  # Field name made lowercase.
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'user'

class Recipe(models.Model):
    recipeid = models.IntegerField(db_column='RecipeID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    mealtype = models.CharField(db_column='MealType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cuisine = models.CharField(db_column='Cuisine', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'recipe'

class Dietrestriction(models.Model):
    restrictionid = models.AutoField(db_column='RestrictionID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dietrestriction'

class Ingredient(models.Model):
    ingredientid = models.AutoField(db_column='IngredientID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', unique=True, max_length=100)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ingredient'

# Mapping models
class Recipedietrestriction(models.Model):
    mappingid = models.AutoField(db_column='MappingID', primary_key=True)  # Field name made lowercase.
    recipeid = models.ForeignKey(Recipe, models.CASCADE, db_column='RecipeID')  # Field name made lowercase.
    restrictionid = models.ForeignKey(Dietrestriction, models.CASCADE, db_column='RestrictionID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'recipedietrestriction'

class Recipeingredient(models.Model):
    mappingid = models.AutoField(db_column='MappingID', primary_key=True)  # Field name made lowercase.
    recipeid = models.ForeignKey(Recipe, models.CASCADE, db_column='RecipeID')  # Field name made lowercase.
    ingredientid = models.ForeignKey(Ingredient, models.CASCADE, db_column='IngredientID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'recipeingredient'

class Userdietrestriction(models.Model):
    mappingid = models.AutoField(db_column='MappingID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.CASCADE, db_column='UserID')  # Field name made lowercase.
    restrictionid = models.ForeignKey(Dietrestriction, models.CASCADE, db_column='RestrictionID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'userdietrestriction'

class Userrecipe(models.Model):
    mappingid = models.AutoField(db_column='MappingID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.CASCADE, db_column='UserID')  # Field name made lowercase.
    recipeid = models.ForeignKey(Recipe, models.CASCADE, db_column='RecipeID')  # Field name made lowercase.
    datetime = models.DateTimeField(db_column='Datetime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'userrecipe'
