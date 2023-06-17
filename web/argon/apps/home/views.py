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
from .decorators import post_request_only
import re, html, json, math

# Initialise global MongoDB connections
mongo_client, mongo_conn = settings.get_mongodb()
instructions_collection = mongo_conn['Instructions']
reviews_collection = mongo_conn['Reviews']
nutrition_collection = mongo_conn['Nutrition']

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

    context = {'recipes': recipes}
    return render(request, 'recipe/index.html', context)

@login_required(login_url="/login/")
def view_recipe(request, id):
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

    return render(request, 'recipe/view_recipe.html', context)

@login_required(login_url="/login/")
def add_to_user_recipe(request, recipe_id):
    if request.method == 'POST':
        user_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO userrecipe (UserID, RecipeID) VALUES (%s, %s)", [user_id, recipe_id])
        return redirect('recipe', recipe_id=recipe_id)
    else:
        return redirect('home')

@login_required(login_url="/login/")
def search_recipes(request):
    """ 
    Base SQL (view all recipes):
    SELECT RecipeID, Name, Description, MealType, Cuisine 
    FROM recipe 
    ORDER BY RecipeID ASC
    LIMIT 12
    OFFSET xx
    """

    # Initialise context variables
    recipe_count = None
    cuisine_count = None
    review_count = None
    review_score = None
    recipes = []
    suggested_ingredients = []
    dietary_restrictions = {'active': [], 'inactive': []}

    # Get context values
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM recipe;")
        recipe_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT(Cuisine)) FROM recipe;")
        cuisine_count = cursor.fetchone()[0]
        cursor.execute("SELECT RecipeID, Name, Description, MealType, Cuisine FROM recipe ORDER BY RecipeID ASC LIMIT 12 OFFSET 0;")
        rows = cursor.fetchall()
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
        cursor.execute("SELECT name FROM ingredient ORDER BY RAND() LIMIT 20;")
        rows = cursor.fetchall()
        for row in rows:
            suggested_ingredients.append(row[0])
        cursor.execute("SELECT u.RestrictionID, d.Name FROM userdietrestriction u, dietrestriction d WHERE u.RestrictionID = d.RestrictionID AND u.UserID = " + str(request.user.id))
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            restriction = {
                'RestrictionID': row[0],
                'Name': row[1]    
            }
            dietary_restrictions['active'].append(restriction)
        cursor.execute("SELECT RestrictionID, Name FROM dietrestriction")
        rows = cursor.fetchall()
        for row in rows:
            restriction = {
                'RestrictionID': row[0],
                'Name': row[1]    
            }
            if(restriction not in dietary_restrictions['active']):
                dietary_restrictions['inactive'].append(restriction)

    review_count = reviews_collection.count_documents({})
    review_score = reviews_collection.aggregate([{'$group': {'_id': None, 'avg_rating': {'$avg': '$Overall_Rating'} } }, {'$project': {'_id': 0, 'avg_rating': {'$round': ['$avg_rating',2] } } }]).next()['avg_rating']

    # Prepare context
    context = {
                'segment': 'search_recipe',
                'results': {
                        'recipe_count': recipe_count,
                        'cuisine_count': cuisine_count,
                        'review_count': review_count,
                        'review_score': review_score,
                        'page_count': math.ceil(recipe_count / 12),
                        'pages': [ i for i in range(1, math.ceil(recipe_count / 12) + 1)],
                        'current_page': 1
                    },
                'recipes': recipes,
                'suggested_ingredients': suggested_ingredients,
                'dietary_restrictions': dietary_restrictions
            }

    # Render template
    html_template = loader.get_template('recipe/search.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@post_request_only
def get_suggested_ingredients(request):
    # Initialise context variables
    suggested_ingredients = []

    # Get context values
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM ingredient ORDER BY RAND() LIMIT 20;")
        rows = cursor.fetchall()
        for row in rows:
            suggested_ingredients.append(row[0])

    # Prepare context
    json_response = {
                'suggested_ingredients': suggested_ingredients
            }

    # Return response
    json_response = json.dumps(json_response)
    # Return response
    return HttpResponse (json_response, content_type='application/json;charset=utf-8')

@login_required(login_url="/login/")  
@post_request_only
def process_search (request): 
    """ 
    Base SQL (Normal Mode):
    SELECT r1.RecipeID, r1.Name, r1.Description, r1.MealType, r1.Cuisine
    FROM recipe r1
    WHERE r1.RecipeID IN (
        SELECT DISTINCT r2.RecipeID
        FROM recipe r2
        JOIN recipeingredient ri ON r2.RecipeID = ri.RecipeID
        JOIN ingredient i ON i.IngredientID = ri.IngredientID
        WHERE i.Name LIKE '%fish%' OR i.Name LIKE '%chicken%'
    )
    ORDER BY r1.RecipeID ASC
    LIMIT 12
    OFFSET 0;
    
    -----

    Base SQL (Strict Mode):
    SELECT r1.RecipeID, r1.Name, r1.Description, r1.MealType, r1.Cuisine
    FROM recipe r1
    WHERE r1.RecipeID IN (
        SELECT DISTINCT r3.RecipeID
        FROM recipe r3
        JOIN recipeingredient ri2 ON r3.RecipeID = ri2.RecipeID
        WHERE r3.RecipeID IN (
        SELECT DISTINCT r2.RecipeID
        FROM recipe r2
        JOIN recipeingredient ri ON r2.RecipeID = ri.RecipeID
        JOIN ingredient i ON i.IngredientID = ri.IngredientID
        WHERE i.Name LIKE '%fish%' OR i.Name LIKE '%chicken%'
        )
        GROUP BY r3.RecipeID
        HAVING COUNT(ri2.MappingID) <= 15
    )
    ORDER BY r1.RecipeID ASC
    LIMIT 12
    OFFSET 0;

    -----

    Advanced search:
    SELECT DISTINCT(RecipeIngredient.RecipeID)
    FROM RecipeIngredient
    WHERE RecipeIngredient.IngredientID IN (SELECT Ingredient.IngredientID
    FROM Ingredient
    WHERE Ingredient.Name LIKE '%chilli%'
        OR Ingredient.Name LIKE '%rice%'
        OR Ingredient.Name LIKE '%salt%')
    AND RecipeIngredient.RecipeID NOT IN (SELECT RecipeID
    FROM RecipeDietaryRestriction
    WHERE DietaryRestrictionID IN (SELECT DietaryRestrictionID FROM UserDietaryRestriction WHERE UserID = X));
    """
    
    # Get POST data
    request_type = request.POST.get("type", "")                                 # Request type
    list_search_terms = json.loads(request.POST.get("search", "[]"))            # Search terms
    requested_page = int(request.POST.get("page", 0))                           # Requested page number
    offset = (requested_page - 1) * 12                                          # Requested row offset
    strict_mode = int(request.POST.get("strict_mode", 0))                       # Search mode (strict or normal)
    list_restrictions = json.loads(request.POST.get("restrictions", "[]"))      # Dietary restrictions

    # Initialise context variables
    recipe_count = None
    cuisine_count = None
    review_count = None
    review_score = None
    recipes = []
    
    # Prepare queries
    search_query = "SELECT r1.RecipeID, r1.Name, r1.Description, r1.MealType, r1.Cuisine FROM recipe r1 "  
    if(strict_mode):
        base_query = "SELECT DISTINCT r3.RecipeID FROM recipe r3 JOIN recipeingredient ri2 ON r3.RecipeID = ri2.RecipeID WHERE r3.RecipeID IN (SELECT DISTINCT r2.RecipeID FROM recipe r2 JOIN recipeingredient ri ON r2.RecipeID = ri.RecipeID JOIN ingredient i ON i.IngredientID = ri.IngredientID WHERE %s) GROUP BY r3.RecipeID HAVING COUNT(ri2.MappingID) <= %s"
    else:
        base_query = "SELECT DISTINCT r2.RecipeID FROM recipe r2 JOIN recipeingredient ri ON r2.RecipeID = ri.RecipeID JOIN ingredient i ON i.IngredientID = ri.IngredientID WHERE "

    # Check search terms
    if(list_search_terms):
        # Parse search items
        list_search_terms = ["i.Name LIKE '%%%s%%'" % i for i in list_search_terms]
        search = ' OR '.join(list_search_terms)
        if(strict_mode):
            base_query = base_query % (search, str(len(list_search_terms)))
        else:
            base_query += search
        search_query += "WHERE r1.RecipeID IN (%s) " % base_query
        count_query = "SELECT COUNT(DISTINCT(temp.RecipeID)), COUNT(DISTINCT(temp.Cuisine)) FROM (" + search_query + ") temp;"
        search_query += "ORDER BY r1.RecipeID ASC LIMIT 12 OFFSET %s;" % offset
    else:
        # No search items
        count_query = "SELECT COUNT(*), COUNT(DISTINCT(Cuisine)) FROM recipe;"
        search_query += "ORDER BY r1.RecipeID ASC LIMIT 12 OFFSET %s;" % offset

    # Get context values
    with connection.cursor() as cursor:
        # Get recipe and cuisine count
        cursor.execute(count_query)
        results = cursor.fetchone()
        recipe_count = results[0]
        cuisine_count = results[1]

        # Get recipes
        cursor.execute(search_query)
        rows = cursor.fetchall()
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

        # CGet review count and score
        if(list_search_terms):
            # Get target recipes
            list_recipes = []
            cursor.execute(base_query)
            rows = cursor.fetchall()
            for row in rows:
                list_recipes.append(row[0])
            # Get review results
            review_results = reviews_collection.aggregate([
                                {'$match': {'RecipeID': {'$in': list_recipes} } },
                                {'$facet': {'total_reviews': [{'$count': 'count'}], 'average_rating': [{'$group': {'_id': None, 'avg_rating': {'$avg': '$Overall_Rating'} } } ] } },
                                {'$project': {'_id': 0, 'review_count': {'$arrayElemAt': ['$total_reviews.count', 0]}, 'avg_rating': {'$round': [{'$arrayElemAt': ['$average_rating.avg_rating', 0]}, 2] } } }
                            ]).next()
            # Check for results
            if(len(review_results.keys()) != 2):
                review_count = 0
                review_score = 0
            else:
                review_count = review_results['review_count']
                review_score = review_results['avg_rating']
        else:
            review_count = reviews_collection.count_documents({})
            review_score = reviews_collection.aggregate([
                                {'$group': {'_id': None, 'avg_rating': {'$avg': '$Overall_Rating'} } }, 
                                {'$project': {'_id': 0, 'avg_rating': {'$round': ['$avg_rating',2] } } }
                            ]).next()['avg_rating']

    # Prepare context
    json_response = {
                'segment': 'search_recipe',
                'results': {
                        'recipe_count': recipe_count,
                        'cuisine_count': cuisine_count,
                        'review_count': review_count,
                        'review_score': review_score,
                        'page_count': math.ceil(recipe_count / 12),
                        'pages': [i for i in range(1, math.ceil(recipe_count / 12) + 1)],
                        'current_page': requested_page
                    },
                'recipes': recipes
            }

    # Debugging
    print("POST Data:")
    print("Type:", request_type)
    print("Strict Mode:", strict_mode)
    print("Requested page:", requested_page)
    print("Page offset:", offset)
    print("Search terms:", list_search_terms)
    print("Dietary Restrictions:", list_restrictions)
    print("Search SQL:", search_query)
    print("Count SQL:", count_query)
    # print("Response:", json_response)

    # Return response
    json_response = json.dumps(json_response)
    # Return response
    return HttpResponse (json_response, content_type='application/json;charset=utf-8')

from django.shortcuts import render, redirect
from pymongo import MongoClient

@login_required(login_url="/login/")  
def add_review(request, recipe_id):
    if request.method == 'POST':
        name = request.POST['name']
        rating = request.POST['rating']
        text = request.POST['text']
        
        # Connect to MongoDB
        client = MongoClient('mongodb+srv://admin:admin@zerowastekitchen.damsz1o.mongodb.net/?authMechanism=SCRAM-SHA-1')
        db = client['INF2005_DB']
        collection = db['Reviews']
        
        review = {
            'Name': name,
            'Rating': rating,
            'Text': text,
            'UserID': request.user.id  # Assuming you have implemented authentication and the user is logged in
        }
        
        # Find the recipe document by RecipeID
        recipe = collection.find_one({'RecipeID': recipe_id})
        
        if recipe is None:
            # If the recipe doesn't exist, create a new document
            recipe = {
                'RecipeID': recipe_id,
                'Reviews': [review]
            }
            collection.insert_one(recipe)
        else:
            # If the recipe exists, append the new review to the existing array
            collection.update_one({'RecipeID': recipe_id}, {'$push': {'Reviews': review}})
        
        return redirect('recipe_details', recipe_id=recipe_id)
    
    return render(request, 'recipe_details.html')

