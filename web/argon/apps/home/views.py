# -*- encoding: utf-8 -*-
import re
import html
import json
import math
import gridfs
import pathlib
import base64
from redis.commands.json.path import Path
from hashlib import sha256
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
from django.contrib import messages
from pymongo import MongoClient
from pymongo.cursor import CursorType

# Initialise global MongoDB connections
mongo_client, mongo_conn = settings.get_mongodb()
instructions_collection = mongo_conn['Instructions']
reviews_collection = mongo_conn['Reviews']
nutrition_collection = mongo_conn['Nutrition']
fs = gridfs.GridFS(mongo_conn)

# Initialise global Redis connection
redis_client = settings.get_redis()

def clean_input(input_value):
    # Decode HTML encoded characters (&amp; -> &)
    input_value = html.unescape(input_value)

    # Remove heading and trailing whitespaces
    input_value = input_value.strip()

    # Remove invalid characters
    input_value = re.sub(r"[\[\];\'\"|\\]", "", input_value)

    # Return cleaned input
    return input_value

def get_hash(value, delimiter=''):
    if(isinstance(value, list)):
        value = delimiter.join(value)
    return sha256(value.encode('utf-8')).hexdigest()

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

# Testing route only
@login_required(login_url="/login/")
def get_recipes(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT RecipeID, Name, Description, COALESCE(`MealType`, 'N/A'), Cuisine FROM recipe ORDER BY RAND() LIMIT 10")
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

    reviews = reviews_data.get('Reviews', []) if reviews_data else []
    for data in reviews:
        file_document = fs.find_one({'reviewID': data['ReviewID']})
        data['mime_type'] = file_document.mime_type if file_document else None
        data['content_type'] = file_document.content_type if file_document else None
        data['file'] = base64.b64encode(file_document.read()).decode('ascii') if file_document else None

    # Define the default image URL
    default_image_url = "/static/assets/img/food/zwk.png"

    # Get the recipe image URL or use the default image URL
    image_url = recipe_data.get('Image', default_image_url)

    # Function to check if a field is empty and return "Not Available"
    def check_field(value):
        if value or value == 0:
            return value
        return "-"

    # Retrieve data from MySQL
    with connections['default'].cursor() as cursor:
        cursor.execute(
            "SELECT Name, Description, MealType, Cuisine FROM recipe WHERE RecipeID = %s", [id])
        mysql_data = cursor.fetchone()

    # Combine the data from SQL and MongoDB
    context = {
        'recipe': {
            'RecipeID': id,
            'Name': check_field(mysql_data[0]),
            'Description': check_field(mysql_data[1]),
            # Add the 'MealType' field from MySQL
            'MealType': check_field(mysql_data[2]),
            # Add the 'Cuisine' field from MySQL
            'Cuisine': check_field(mysql_data[3]),
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
            'Reviews': reviews,
            'Overall_Rating': check_field(reviews_data.get('Overall_Rating')) if reviews_data else None,
        },
        'segment'  : 'search_recipe'
    }

    return render(request, 'recipe/view_recipe.html', context)

@login_required(login_url="/login/")
def add_to_user_recipe(request, recipe_id):
    if request.method == 'POST':
        user_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO userrecipe (UserID, RecipeID) VALUES (%s, %s)", [user_id, recipe_id])
            response_data = {
                'success': True
            }
            json_response = json.dumps(response_data)
        return HttpResponse(json_response, content_type='application/json;charset=utf-8')
    else:
        return redirect('home')

@login_required(login_url="/login/")
def search_recipes(request):
    """ 
    Query Structure:
    count_sql
        base_sql
        query_sql
            diet_sql
        offset_sql

    Count:
    SELECT COUNT(DISTINCT(count_results.RecipeID)), COUNT(DISTINCT(count_results.Cuisine)) FROM (

        Base search:
        SELECT base_r.RecipeID, base_r.Name, base_r.Description, base_r.MealType, base_r.Cuisine FROM recipe base_r

        Query:
        WHERE base_r.RecipeID NOT IN (
            Diet restriction:
            SELECT DISTINCT diet_r.RecipeID
            FROM recipe diet_r, recipedietrestriction diet_rdp
            WHERE diet_r.RecipeID = diet_rdp.RecipeID 
            AND diet_rdp.RestrictionID IN (%s, %s)
        )

        Offset:
        ORDER BY base_r.RecipeID ASC LIMIT 12 OFFSET 0;
    
    ) count_results
    """

    # Initialise context variables
    recipe_count = None
    cuisine_count = None
    review_count = None
    review_score = None
    recipes = []
    suggested_ingredients = []
    dietary_restrictions = {'active': [], 'inactive': []}

    # Get user session data, if any
    if('last_search' in request.session):
        print("Restored session!")
        # Restore user session values
        context = request.session['last_search']
        active_restrictions = request.session['last_search']['dietary_restrictions']

        # Get context values
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM ingredient ORDER BY RAND() LIMIT 20;")
            rows = cursor.fetchall()
            for row in rows:
                suggested_ingredients.append(row[0])
            cursor.execute("SELECT RestrictionID, Name FROM dietrestriction")
            rows = cursor.fetchall()
            for row in rows:
                restriction = {
                    'RestrictionID': row[0],
                    'Name': row[1]    
                }
                if(str(row[0]) in active_restrictions):
                    dietary_restrictions['active'].append(restriction)
                else:
                    dietary_restrictions['inactive'].append(restriction)
        
        # Update context
        context['suggested_ingredients'] = suggested_ingredients
        context['dietary_restrictions'] = dietary_restrictions
    else:
        # Get context values
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM ingredient ORDER BY RAND() LIMIT 20;")
            rows = cursor.fetchall()
            for row in rows:
                suggested_ingredients.append(row[0])
            cursor.execute("SELECT u.RestrictionID, d.Name FROM userdietrestriction u, dietrestriction d WHERE u.RestrictionID = d.RestrictionID AND u.UserID = " + str(request.user.id))
            rows = cursor.fetchall()
            for row in rows:
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
            
            # Check if user has any active dietary restrictions
            if(dietary_restrictions['active']):
                print("User with dietary restrictions!")
                # Initialise queries
                count_sql = "SELECT COUNT(DISTINCT(count_results.RecipeID)), COUNT(DISTINCT(count_results.Cuisine)) FROM (%s) count_results"
                base_sql = "SELECT base_r.RecipeID, base_r.Name, base_r.Description, base_r.MealType, base_r.Cuisine FROM recipe base_r"
                diet_sql = "SELECT DISTINCT diet_r.RecipeID FROM recipe diet_r, recipedietrestriction diet_rdp WHERE diet_r.RecipeID = diet_rdp.RecipeID AND diet_rdp.RestrictionID IN (%s)"
                offset_sql = "ORDER BY base_r.RecipeID ASC LIMIT 12 OFFSET 0"

                # Parse queries
                restrictions = ', '.join(str(i['RestrictionID']) for i in dietary_restrictions['active'])
                diet_sql = diet_sql % restrictions
                query_sql = "WHERE base_r.RecipeID NOT IN (%s)" % (diet_sql)
                sql = base_sql + " " + query_sql
                count_sql = count_sql % (sql)
                recipes_sql = sql
                sql = sql + " " + offset_sql

                # Get recipe and cuisine count
                cursor.execute(count_sql)
                results = cursor.fetchone()
                recipe_count = results[0]
                cuisine_count = results[1]

                # Get recipes
                cursor.execute(sql)
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

                # Get review count and score
                # Get target recipes
                list_recipes = []
                cursor.execute(recipes_sql)
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
                print("User without dietary restrictions!")
                cursor.execute("SELECT COUNT(DISTINCT(RecipeID)), COUNT(DISTINCT(Cuisine)) FROM recipe;")
                results = cursor.fetchone()
                recipe_count = results[0]
                cuisine_count = results[1]
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
def process_search (request): 
    """ 
    Query Structure:
    count_sql
        base_sql
        query_sql
            strict_sql
                inner_query
                    normal_sql
                    diet_sql
        offset_sql

    Count:
    SELECT COUNT(DISTINCT(count_results.RecipeID)), COUNT(DISTINCT(count_results.Cuisine)) FROM (

        Base search:
        SELECT base_r.RecipeID, base_r.Name, base_r.Description, base_r.MealType, base_r.Cuisine FROM recipe base_r

        Query:
        WHERE base_r.RecipeID IN (

            Strict search
            SELECT DISTINCT strict_r.RecipeID
            FROM recipe strict_r
            JOIN recipeingredient strict_ri ON strict_r.RecipeID = strict_ri.RecipeID
            WHERE strict_r.RecipeID IN (

                Inner query:
                    Normal search:
                    SELECT DISTINCT normal_r.RecipeID
                    FROM recipe normal_r
                    JOIN recipeingredient normal_ri ON normal_r.RecipeID = normal_ri.RecipeID
                    JOIN ingredient normal_i ON normal_i.IngredientID = normal_ri.IngredientID
                    WHERE normal_i.Name LIKE '%fish%' OR normal_i.Name LIKE '%chicken%'

                    Diet restriction:
                    EXCEPT
                    SELECT DISTINCT diet_r.RecipeID
                    FROM recipe diet_r, recipedietrestriction diet_rdp
                    WHERE diet_r.RecipeID = diet_rdp.RecipeID 
                    AND diet_rdp.RestrictionID IN (%s, %s)

            )
            GROUP BY strict_r.RecipeID
            HAVING COUNT(strict_ri.MappingID) <= %s

        )

        Offset:
        ORDER BY base_r.RecipeID ASC LIMIT 12 OFFSET %s;
    
    ) count_results
    """
    
    # Get POST data
    request_type = request.POST.get("type", "")                                         # Request type
    list_search_terms = sorted(json.loads(request.POST.get("search", "[]")))            # Search terms
    requested_page = int(request.POST.get("page", 0))                                   # Requested page number
    offset = (requested_page - 1) * 12                                                  # Requested row offset
    strict_mode = int(request.POST.get("strict_mode", 0))                               # Search mode (strict or normal)
    list_restrictions = sorted(json.loads(request.POST.get("restrictions", "[]")))      # Dietary restrictions

    # Initialise context variables
    recipe_count = None
    cuisine_count = None
    review_count = None
    review_score = None
    recipes = []

    # Initialise SQL
    count_sql = "SELECT COUNT(DISTINCT(count_results.RecipeID)), COUNT(DISTINCT(count_results.Cuisine)) FROM (%s) count_results"
    base_sql = "SELECT base_r.RecipeID, base_r.Name, base_r.Description, base_r.MealType, base_r.Cuisine FROM recipe base_r"
    strict_sql = "SELECT DISTINCT strict_r.RecipeID FROM recipe strict_r JOIN recipeingredient strict_ri ON strict_r.RecipeID = strict_ri.RecipeID WHERE strict_r.RecipeID IN (%s) GROUP BY strict_r.RecipeID HAVING COUNT(strict_ri.MappingID) <= %s"
    normal_sql = "SELECT DISTINCT normal_r.RecipeID FROM recipe normal_r JOIN recipeingredient normal_ri ON normal_r.RecipeID = normal_ri.RecipeID JOIN ingredient normal_i ON normal_i.IngredientID = normal_ri.IngredientID WHERE %s"
    diet_sql = "EXCEPT SELECT DISTINCT diet_r.RecipeID FROM recipe diet_r, recipedietrestriction diet_rdp WHERE diet_r.RecipeID = diet_rdp.RecipeID AND diet_rdp.RestrictionID IN (%s)"
    offset_sql = "ORDER BY base_r.RecipeID ASC LIMIT 12 OFFSET %s"
    inner_query = ""
    inner_query_results = []

    """ Parse query SQL """
    # Check for search terms
    if(list_search_terms):
        # Initialise query
        query_sql = "WHERE base_r.RecipeID IN (%s)"

        # Parse search items
        search_terms = ["normal_i.Name LIKE '%%%s%%'" % clean_input(i) for i in list_search_terms]
        searches = ' OR '.join(search_terms)
        # Parse normal search SQL
        normal_sql = normal_sql % searches

        # Check dietary restrictions
        if(list_restrictions):
            restrictions = ', '.join(list_restrictions)
            # Parse diet SQL
            diet_sql = diet_sql % restrictions

        # Prepare inner subquery
        if(list_restrictions):
            inner_query = normal_sql + " " + diet_sql
        else:
            inner_query = normal_sql

        # Get generated hash key for inner query
        inner_query_key = get_hash(list_search_terms + list_restrictions)

        # Check if inner subquery results have been cached
        inner_query_value = redis_client.json().get(inner_query_key)
        if(not inner_query_value):
            # Get results of inner query
            with connection.cursor() as cursor:
                # Get recipes
                cursor.execute(inner_query)
                rows = cursor.fetchall()
                for row in rows:
                    inner_query_results.append(row[0])

            # Parse inner query into JSON for storage in Redis cache
            inner_query_value = {   
                                    'list_search_terms': list_search_terms,
                                    'list_restrictions': list_restrictions,
                                    'results': inner_query_results
                                } 

            # Cache inner query results
            redis_client.json().set(inner_query_key, Path.root_path(), inner_query_value)
        else:
            inner_query_results = inner_query_value['results']
            print("Cached results:", inner_query_results)

        # Parse cached results
        inner_query_results = [str(i) for i in inner_query_results]
        cached = ', '.join(inner_query_results) if inner_query_results else '0' # 0 is a predefined RecipeID that guarantees no matches

        # Check strict mode
        if(strict_mode):
            # Parse strict SQL
            strict_sql = strict_sql % (cached, str(len(list_search_terms)))
            # Parse query SQL
            query_sql = query_sql % strict_sql
        else:
            # Parse query SQL
            query_sql = query_sql % (cached)
    else:
        # Initialise query
        query_sql = ""

        # Check dietary restrictions
        if(list_restrictions):
            restrictions = ', '.join(list_restrictions)
            # Parse diet SQL
            diet_sql = diet_sql % restrictions
            query_sql = "WHERE base_r.RecipeID NOT IN (%s)" % (diet_sql.replace("EXCEPT ", ""))

    """ Parse offset SQL """
    offset_sql = offset_sql % (offset)

    """ Parse queries """
    sql = base_sql + " " + query_sql
    count_sql = count_sql % (sql)
    recipes_sql = sql
    sql = sql + " " + offset_sql

    # Get context values
    with connection.cursor() as cursor:
        # Get recipe and cuisine count
        cursor.execute(count_sql)
        results = cursor.fetchone()
        recipe_count = results[0]
        cuisine_count = results[1]

        # Get recipes
        cursor.execute(sql)
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

        # Get review count and score
        if(list_search_terms):
            # Get target recipes
            list_recipes = []
            cursor.execute(recipes_sql)
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
                'recipes': recipes,
                'dietary_restrictions': list_restrictions,
                'strict_mode': strict_mode,
                'searches': list_search_terms
            }

    # Save context to user's session
    request.session['last_search'] = json_response

    # Debugging
    print("POST Data:")
    print("Type:", request_type)
    print("Strict Mode:", strict_mode)
    print("Requested page:", requested_page)
    print("Page offset:", offset)
    print("Search terms:", list_search_terms)
    print("Dietary Restrictions:", list_restrictions)
    print("Inner Query:", inner_query)
    print("Search SQL:", sql)
    print("Count SQL:", count_sql)
    # print("Response:", json_response)

    # Return response
    json_response = json.dumps(json_response)
    # Return response
    return HttpResponse (json_response, content_type='application/json;charset=utf-8')

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
def add_review(request, recipe_id):
    if request.method == 'POST':
        name = request.user.username
        rating = int(request.POST['rating'])
        text = request.POST['text']

        # Check if the user has made the recipe
        user_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM userrecipe WHERE UserID = %s AND RecipeID = %s", [user_id, recipe_id])
            recipe_exists = cursor.fetchone() is not None

        if recipe_exists:
            img = request.FILES.get('img')
            review_id = generate_review_id(recipe_id)

            # Handle the file
            if img:
                # Validate fiile size
                max_size = 20 * 1024 * 1024
                if img.size > max_size:
                    response = {
                        'made'       : True,
                        'valid_file' : False,
                        'reason'     : "File too large! Max size of 20MB."
                    }
                    json_response = json.dumps(response)
                    # Return response
                    return HttpResponse (json_response, content_type='application/json;charset=utf-8')
                
                img_data = img.read()

                # Get the extension
                extension = pathlib.Path(img.name).suffix
                mime_type = img.content_type
                content_type = mime_type.split('/')[0]

                # Validate fiile type 
                if content_type not in ['image', 'video']:
                    response = {
                        'made'       : True,
                        'valid_file' : False,
                        'reason'     : "Invalid file type! Only submit a photo or video."
                    }
                    json_response = json.dumps(response)
                    # Return response
                    return HttpResponse (json_response, content_type='application/json;charset=utf-8')

                filename = str(review_id) + extension
                # Save the file in gridFS
                fs.put(img_data, filename=filename, mime_type=mime_type, content_type=content_type, reviewID=review_id)

            review = {
                'ReviewID': review_id,
                'Name': name,
                'Rating': rating,
                'Text': text,
                'UserID': user_id
            }

            # Find the recipe document by RecipeID
            recipe = reviews_collection.find_one({'RecipeID': recipe_id})

            if recipe is None:
                # If the recipe doesn't exist, create a new document
                recipe = {
                    'RecipeID': recipe_id,
                    'Reviews': [review],
                    'Overall_Rating': rating  # Set initial overall rating to the first review's rating
                }
                reviews_collection.insert_one(recipe)
            else:
                # If the recipe exists, append the new review to the existing array
                reviews_collection.update_one(
                    {'RecipeID': recipe_id},
                    {'$push':
                        {'Reviews': review}
                     }
                )

                # Update overall rating
                reviews_collection.update_one(
                    {'RecipeID': recipe_id},
                    [
                        {
                            '$set': {
                                'Overall_Rating': {
                                    '$avg': '$Reviews.Rating'
                                }
                            }
                        }
                    ]
                )

            response = {
                'made'       : True,
                'valid_file' : True
            }
            json_response = json.dumps(response)
            # Return response
            return HttpResponse (json_response, content_type='application/json;charset=utf-8')
        else:

            response = {
                'made' : False
            }
            # User hasn't made the recipe, show an error message
            json_response = json.dumps(response)

            return HttpResponse (json_response, content_type='application/json;charset=utf-8')
    else:
        return render(request, 'recipe/view_recipe.html')

def generate_review_id(recipe_id):
    recipe = reviews_collection.find_one({'RecipeID': recipe_id})
    if recipe:
        reviews = recipe['Reviews']
        if reviews:
            last_review = max(reviews, key=lambda review: review.get('ReviewID', 0))
            last_review_id = last_review.get('ReviewID', 0)
            new_review_id_num = int(last_review_id) + 1
            return new_review_id_num

    recipe_id_prefix = str(recipe_id)[:5]
    new_review_id_num = int(f"{recipe_id_prefix}000") + 1

    return new_review_id_num