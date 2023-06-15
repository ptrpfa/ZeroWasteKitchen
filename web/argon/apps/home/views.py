# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db import connection
from django.shortcuts import render
from core import settings
from django.db import connections
import re, html, json

def clean_input (input_value):
        
    # Decode HTML encoded characters (&amp; -> &)
    input_value = html.unescape (input_value)

    # Remove heading and trailing whitespaces
    input_value = input_value.strip ()

    # Remove invalid characters
    input_value = re.sub (r"[\[\];\'\"|\\]", "", input_value) 

    # Return cleaned input
    return input_value

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
  
@login_required(login_url="/login/")
def get_recipes(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT RecipeID, Name, Description, COALESCE(`MealType`, 'N/A'), Cuisine FROM recipe ORDER BY RAND() LIMIT 10")
        rows = cursor.fetchall()

    # Connect to MongoDB
    mongo_client, mongo_conn = settings.get_mongodb()
    instructions_collection = mongo_conn['Instructions']

    recipes = []
    for row in rows:
        recipe_id = row[0]
        instruction = instructions_collection.find_one({'RecipeID': recipe_id})
        image_url = instruction.get('Image', "/static/assets/img/food/zwk.png")

        recipe = {
            'RecipeID': recipe_id,
            'Name': row[1],
            'Description': row[2],
            'MealType': row[3],
            'Cuisine': row[4],
            'Image': image_url,
        }
        recipes.append(recipe)

    # Close the MongoDB client
    mongo_client.close()

    context = {'recipes': recipes}
    return render(request, 'recipe/index.html', context)

@login_required(login_url="/login/")
def view_recipe(request, id):
    # Get the 'Instructions' collection from MongoDB
    mongo_client, mongo_conn = settings.get_mongodb()
    instructions_collection = mongo_conn['Instructions']
    nutrition_collection = mongo_conn['Nutrition']
    reviews_collection = mongo_conn['Reviews']

    # Query the 'Instructions' collection for the recipe with the specified RecipeID
    recipe_data = instructions_collection.find_one({'RecipeID': id})
    
    # Query the 'Nutrition' collection for the nutrition information of the recipe
    nutrition_data = nutrition_collection.find_one({'RecipeID': id})
    
    # Query the 'Reviews' collection for the reviews of the recipe
    reviews_data = reviews_collection.find_one({'RecipeID': id})

    # Define the default image URL
    default_image_url = "/static/assets/img/food/zwk.png"

    # Get the recipe image URL or use the default image URL
    image_url = recipe_data.get('Image', default_image_url)

    # Function to check if a field is empty and return "Not Available"
    def check_field(value):
        return value if value else "Not Available"

    # Retrieve data from MySQL
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT Name, Description, MealType, Cuisine FROM recipe WHERE RecipeID = %s", [id])
        mysql_data = cursor.fetchone()
    
    # Combine the data from SQL and MongoDB 
    context = {
        'recipe': {
            'RecipeID': id,
            'Name': check_field(mysql_data[0]),               
            'Description': check_field(mysql_data[1]),       
            'MealType': check_field(mysql_data[2]),  # Add the 'MealType' field from MySQL
            'Cuisine': check_field(mysql_data[3]),   # Add the 'Cuisine' field from MySQL
            'IngredientLines': recipe_data.get('Ingredient_Lines', []),
            'Instructions': recipe_data.get('Instructions', []),
            'TotalTime': check_field(recipe_data.get('Total_Time')),
            'Steps': check_field(recipe_data.get('Steps')),
            'Image': image_url,
            'Servings': check_field(nutrition_data.get('Servings')),
            'Calories': check_field(nutrition_data.get('Calories')),
            'Fats': check_field(nutrition_data.get('Total_Fats')),
            'Sodium': check_field(nutrition_data.get('Sodium')),
            'Carbohydrates': check_field(nutrition_data.get('Carbohydrates')),
            'Protein': check_field(nutrition_data.get('Protein')),
            'Reviews': reviews_data.get('Reviews', []) if reviews_data else [],
            'Overall_Rating': check_field(reviews_data.get('Overall_Rating')) if reviews_data else '- '
        }
    }

    # Close the MongoDB client
    mongo_client.close()

    return render(request, 'recipe/view_recipe.html', context)


@login_required(login_url="/login/")
def search_recipes(request):
    # Get MongoDB connections
    mongo_client, mongo_conn = settings.get_mongodb()
    reviews = mongo_conn['Reviews']
    instructions = mongo_conn['Instructions']

    # Initialise context variables
    recipe_count = None
    cuisine_count = None
    review_count = None
    review_score = None
    recipes = []

    # Get context values
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM recipe;")
        recipe_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT(Cuisine)) FROM recipe;")
        cuisine_count = cursor.fetchone()[0]
        cursor.execute("SELECT RecipeID, Name, Description, COALESCE(`MealType`, 'N/A'), Cuisine FROM recipe ORDER BY RecipeID LIMIT 12")
        rows = cursor.fetchall()

    for row in rows:
        recipe_id = row[0]
        instruction = instructions.find_one({'RecipeID': recipe_id})
        image_url = instruction.get('Image', "/static/assets/img/food/zwk.png")

        recipe = {
            'RecipeID': recipe_id,
            'Name': row[1],
            'Description': row[2],
            'MealType': row[3],
            'Cuisine': row[4],
            'Image': image_url,
        }
        recipes.append(recipe)

    review_count = reviews.count_documents({})
    review_score = reviews.aggregate([{'$group': {'_id': None, 'avg_rating': {'$avg': '$Overall_Rating'} } }, {'$project': {'_id': 0, 'avg_rating': {'$round': ['$avg_rating',2] } } }]).next()['avg_rating']

    # Prepare context
    context = {
                'segment': 'search_recipe',
                'results': {
                        'recipe_count': recipe_count,
                        'cuisine_count': cuisine_count,
                        'review_count': review_count,
                        'review_score': review_score,
                    },
                'recipes': recipes
            }

    # Close connections
    mongo_client.close()

    # Render template
    html_template = loader.get_template('recipe/search.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")  
def process_search (request):  # View for processing search
    return {"hello"}

def add_to_user_recipe(request, recipe_id):
    if request.method == 'POST':
        user_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO userrecipe (UserID, RecipeID) VALUES (%s, %s)", [user_id, recipe_id])
        return redirect('recipe', recipe_id=recipe_id)
    else:
        return redirect('home')
