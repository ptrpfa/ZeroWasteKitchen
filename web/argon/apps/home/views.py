# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Recipe
from django.db import connection
from django.shortcuts import render
from core import settings

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
def recipe_view(request, cuisine=None):
    data = [
    {
        'cuisine': 'Italian',
        'dish': 'Pasta',
        'ingredients': [
            'Tomatoes',
            'Basil',
            'Mozzarella',
            'Olive Oil',
            'Garlic',
            'Pasta',
            'Parmesan Cheese',
            'Onions',
            'Bell Peppers',
            'Mushrooms',
        ],
        'ratings': '4.5/5',
        'calorie':'1280Kcal',
        'tags': ['Cuisine: Italian', 'Easy', 'Quick', 'Vegetarian'],
        'difficulty': 'Easy',
        'description': 'Classic Italian pasta dish with fresh tomatoes, basil, and mozzarella.',
        'img': '/static/assets/img/food/pasta.jpeg',
        'instructions': [
            'Cook the pasta according to package instructions.',
            'In a pan, heat olive oil and sauté garlic, onions, bell peppers, and mushrooms.',
            'Add tomatoes, basil, and cooked pasta. Mix well.',
            'Serve hot, garnished with grated Parmesan cheese.',
        ]
    },
    {
        'cuisine': 'Mexican',
        'dish': 'Tacos',
        'ingredients': [
            'Tortillas',
            'Ground Beef',
            'Lettuce',
            'Tomatoes',
            'Cheese',
            'Onions',
            'Cilantro',
            'Lime',
            'Salsa',
            'Sour Cream',
        ],
        'ratings': '4/5',
        'calorie':'1345Kcal',
        'tags': ['Cuisine: Mexican', 'Spicy', 'Street Food'],
        'difficulty': 'Medium',
        'description': 'Flavorful Mexican street-style tacos filled with seasoned ground beef and fresh toppings.',
        'img': '/static/assets/img/food/taco.jpeg',
        'instructions': [
            'Cook ground beef in a skillet until browned.',
            'Warm tortillas in a dry pan or microwave.',
            'Assemble tacos with cooked ground beef, lettuce, tomatoes, cheese, onions, cilantro, and toppings of your choice.',
            'Squeeze lime juice and add salsa and sour cream.',
        ]
    },
    {
        'cuisine': 'Indian',
        'dish': 'Chicken Curry',
        'ingredients': [
            'Chicken',
            'Onions',
            'Tomatoes',
            'Ginger',
            'Garlic',
            'Garam Masala',
            'Turmeric',
            'Cumin',
            'Coriander',
            'Chili Powder',
        ],
        'ratings': '3.4/5',
        'calorie':'3000Kcal',
        'tags': ['Cuisine: Indian', 'Spicy', 'Curry', 'Non-Vegetarian'],
        'difficulty': 'Hard',
        'description': 'Traditional Indian chicken curry with aromatic spices and rich flavors.',
        'img': '/static/assets/img/food/curry.jpeg',
        'instructions': [
            'Marinate chicken with ginger, garlic, turmeric, and chili powder.',
            'In a pan, heat oil and sauté onions until golden brown.',
            'Add tomatoes and spices. Cook until the oil separates.',
            'Add marinated chicken and cook until tender.',
            'Garnish with fresh coriander leaves and serve with rice or naan bread.',
        ]
    },
    {
        'cuisine': 'Chinese',
        'dish': 'Kung Pao Chicken',
        'ingredients': [
            'Chicken',
            'Peanuts',
            'Bell Peppers',
            'Dried Chili Peppers',
            'Garlic',
            'Ginger',
            'Soy Sauce',
            'Vinegar',
            'Sugar',
            'Sesame Oil',
        ],
        'ratings': '5/5',
        'calorie':'3887Kcal',
        'tags': ['Cuisine: Chinese', 'Spicy', 'Stir-fry'],
        'difficulty': 'Medium',
        'description': 'A classic Chinese stir-fry dish with tender chicken, peanuts, and a spicy sauce.',
        'img': '/static/assets/img/food/kung.jpg',
        'instructions': [
            'Marinate chicken with soy sauce, vinegar, and sugar.',
            'In a wok, heat oil and stir-fry chicken until cooked.',
            'Add garlic, ginger, bell peppers, and dried chili peppers. Stir-fry for a few minutes.',
            'Add peanuts and sauce. Cook until the sauce thickens.',
            'Drizzle with sesame oil and serve hot with steamed rice.',
        ]
    },
    {
        'cuisine': 'Thai',
        'dish': 'Green Curry',
        'ingredients': [
            'Chicken',
            'Green Curry Paste',
            'Coconut Milk',
            'Thai Eggplant',
            'Bamboo Shoots',
            'Bell Peppers',
            'Kaffir Lime Leaves',
            'Thai Basil',
            'Fish Sauce',
            'Palm Sugar',
        ],
        'ratings': '3.9/5',
        'calorie':'1802Kcal',
        'tags': ['Cuisine: Thai', 'Spicy', 'Curry'],
        'difficulty': 'Medium',
        'description': 'Authentic Thai green curry with tender chicken, aromatic herbs, and a creamy coconut sauce.',
        'img': '/static/assets/img/food/green.jpeg',
        'instructions': [
            'In a pan, heat green curry paste until fragrant.',
            'Add chicken and cook until browned.',
            'Add coconut milk, Thai eggplant, bamboo shoots, bell peppers, and kaffir lime leaves.',
            'Simmer until the chicken is cooked and the flavors are well combined.',
            'Stir in Thai basil, fish sauce, and palm sugar. Cook for a few more minutes.',
            'Serve hot with steamed rice.',
        ]
    },
]

    filtered_data = data
    if cuisine:
        filtered_data = [recipe for recipe in data if recipe['cuisine'].lower() == cuisine.lower()]

    context = {
        'recipes': filtered_data,
    }

    return render(request, 'recipe/index.html', context)

@login_required(login_url="/login/")
def recipe_details(request):
    data = [
    {
        'cuisine': 'Italian',
        'dish': 'Pasta',
        'ingredients': [
            'Tomatoes',
            'Basil',
            'Mozzarella',
            'Olive Oil',
            'Garlic',
            'Pasta',
            'Parmesan Cheese',
            'Onions',
            'Bell Peppers',
            'Mushrooms',
        ],
        'ratings': '4.5/5',
        'calorie':'1280Kcal',
        'tags': ['Cuisine: Italian', 'Easy', 'Quick', 'Vegetarian'],
        'difficulty': 'Easy',
        'description': 'Classic Italian pasta dish with fresh tomatoes, basil, and mozzarella.',
        'img': '/static/assets/img/food/pasta.jpeg',
        'instructions': [
            'Cook the pasta according to package instructions.',
            'In a pan, heat olive oil and sauté garlic, onions, bell peppers, and mushrooms.',
            'Add tomatoes, basil, and cooked pasta. Mix well.',
            'Serve hot, garnished with grated Parmesan cheese.',
        ]
    },
    {
        'cuisine': 'Mexican',
        'dish': 'Tacos',
        'ingredients': [
            'Tortillas',
            'Ground Beef',
            'Lettuce',
            'Tomatoes',
            'Cheese',
            'Onions',
            'Cilantro',
            'Lime',
            'Salsa',
            'Sour Cream',
        ],
        'ratings': '4/5',
        'calorie':'1345Kcal',
        'tags': ['Cuisine: Mexican', 'Spicy', 'Street Food'],
        'difficulty': 'Medium',
        'description': 'Flavorful Mexican street-style tacos filled with seasoned ground beef and fresh toppings.',
        'img': '/static/assets/img/food/taco.jpeg',
        'instructions': [
            'Cook ground beef in a skillet until browned.',
            'Warm tortillas in a dry pan or microwave.',
            'Assemble tacos with cooked ground beef, lettuce, tomatoes, cheese, onions, cilantro, and toppings of your choice.',
            'Squeeze lime juice and add salsa and sour cream.',
        ]
    },
    {
        'cuisine': 'Indian',
        'dish': 'Chicken Curry',
        'ingredients': [
            'Chicken',
            'Onions',
            'Tomatoes',
            'Ginger',
            'Garlic',
            'Garam Masala',
            'Turmeric',
            'Cumin',
            'Coriander',
            'Chili Powder',
        ],
        'ratings': '3.4/5',
        'calorie':'3000Kcal',
        'tags': ['Cuisine: Indian', 'Spicy', 'Curry', 'Non-Vegetarian'],
        'difficulty': 'Hard',
        'description': 'Traditional Indian chicken curry with aromatic spices and rich flavors.',
        'img': '/static/assets/img/food/curry.jpeg',
        'instructions': [
            'Marinate chicken with ginger, garlic, turmeric, and chili powder.',
            'In a pan, heat oil and sauté onions until golden brown.',
            'Add tomatoes and spices. Cook until the oil separates.',
            'Add marinated chicken and cook until tender.',
            'Garnish with fresh coriander leaves and serve with rice or naan bread.',
        ]
    },
    {
        'cuisine': 'Chinese',
        'dish': 'Kung Pao Chicken',
        'ingredients': [
            'Chicken',
            'Peanuts',
            'Bell Peppers',
            'Dried Chili Peppers',
            'Garlic',
            'Ginger',
            'Soy Sauce',
            'Vinegar',
            'Sugar',
            'Sesame Oil',
        ],
        'ratings': '5/5',
        'calorie':'3887Kcal',
        'tags': ['Cuisine: Chinese', 'Spicy', 'Stir-fry'],
        'difficulty': 'Medium',
        'description': 'A classic Chinese stir-fry dish with tender chicken, peanuts, and a spicy sauce.',
        'img': '/static/assets/img/food/kung.jpg',
        'instructions': [
            'Marinate chicken with soy sauce, vinegar, and sugar.',
            'In a wok, heat oil and stir-fry chicken until cooked.',
            'Add garlic, ginger, bell peppers, and dried chili peppers. Stir-fry for a few minutes.',
            'Add peanuts and sauce. Cook until the sauce thickens.',
            'Drizzle with sesame oil and serve hot with steamed rice.',
        ]
    },
    {
        'cuisine': 'Thai',
        'dish': 'Green Curry',
        'ingredients': [
            'Chicken',
            'Green Curry Paste',
            'Coconut Milk',
            'Thai Eggplant',
            'Bamboo Shoots',
            'Bell Peppers',
            'Kaffir Lime Leaves',
            'Thai Basil',
            'Fish Sauce',
            'Palm Sugar',
        ],
        'ratings': '3.9/5',
        'calorie':'1802Kcal',
        'tags': ['Cuisine: Thai', 'Spicy', 'Curry'],
        'difficulty': 'Medium',
        'description': 'Authentic Thai green curry with tender chicken, aromatic herbs, and a creamy coconut sauce.',
        'img': '/static/assets/img/food/green.jpeg',
        'instructions': [
            'In a pan, heat green curry paste until fragrant.',
            'Add chicken and cook until browned.',
            'Add coconut milk, Thai eggplant, bamboo shoots, bell peppers, and kaffir lime leaves.',
            'Simmer until the chicken is cooked and the flavors are well combined.',
            'Stir in Thai basil, fish sauce, and palm sugar. Cook for a few more minutes.',
            'Serve hot with steamed rice.',
        ]
    },
]
    dish = request.GET.get('dish')  # Retrieve the dish value from the query parameter

    # Find the recipe object that matches the dish value
    recipe = next((item for item in data if item['dish'] == dish), None)

    if recipe:
        context = {
            'recipe': recipe,
        }

        return render(request, 'recipe/details.html', context)  # Render the details.html template with the recipe data
    else:
        # Recipe not found
        return HttpResponse('Recipe not found!')
    
@login_required(login_url="/login/")
def get_recipes(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT RecipeID, Name, Description, COALESCE(`MealType`, 'N/A'), Cuisine FROM recipe ORDER BY RecipeID LIMIT 10")
        rows = cursor.fetchall()

    recipes = []
    for row in rows:
        recipe = {
            'RecipeID': row[0],
            'Name': row[1],
            'Description': row[2],
            'MealType': row[3],
            'Cuisine': row[4],
        }
        recipes.append(recipe)

    context = {'recipes': recipes}
    return render(request, 'recipe/index.html', context)

from django.db import connections

@login_required(login_url="/login/")
def view_recipe(request, id):
    # Get the 'Instructions' collection from MongoDB
    mongo_client, db_conn = settings.get_mongodb()
    instructions_collection = db_conn['Instructions']
    nutrition_collection = db_conn['Nutrition']
    reviews_collection = db_conn['Reviews']

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
    
    # Combine the data from SQL and MongoDB into a single context dictionary
    context = {
        'recipe': {
            'RecipeID': id,
            'Name': check_field(mysql_data[0]),               # Get the Name from MySQL data
            'Description': check_field(mysql_data[1]),        # Get the Description from MySQL data
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
            'OverallRating': check_field(reviews_data.get('OverallRating')) if reviews_data else 'Not Available'
        }
    }

    # Close the MongoDB client
    mongo_client.close()

    return render(request, 'recipe/view_recipe.html', context)
<<<<<<< HEAD

@login_required(login_url="/login/")
def search_recipes(request):
    context = {'segment': 'search_recipe'}

    html_template = loader.get_template('recipe/search.html')
    return HttpResponse(html_template.render(context, request))
=======
>>>>>>> f22be9ae36f92470f698bc107d48d13d9c5fccb8
