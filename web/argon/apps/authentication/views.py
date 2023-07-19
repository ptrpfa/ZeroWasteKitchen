# -*- encoding: utf-8 -*-

# Create your views here.
import gridfs
import base64
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from .models import Userdietrestriction, Dietrestriction,User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from core import settings
import random
from django.core.cache import cache

# Initialise global MongoDB connections
mongo_client, mongo_conn = settings.get_mongodb()
reviews_collection = mongo_conn['Reviews']
nutrition_collection = mongo_conn['Nutrition']
fs = gridfs.GridFS(mongo_conn)

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def register_user(request):
    msg = None
    success = False

    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM dietrestriction")
        rows = cursor.fetchall()

    diet_restrictions = [row[0] for row in rows]

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user object
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            # Save the selected dietary restrictions for the user
            selected_restrictions = request.POST.getlist("diet_restrictions")

            for restrictions in selected_restrictions:
                restriction_names = [name.strip() for name in restrictions.split(",")]

                for restriction_name in restriction_names:
                    restriction, created = Dietrestriction.objects.get_or_create(name=restriction_name)
                    Userdietrestriction.objects.create(userid=user, restrictionid=restriction)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success, "diet_restrictions": diet_restrictions})

@login_required
def update_profile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        
        if "delete_account" in request.POST:
            # Soft delete account set if_active to 0
            user = request.user
            user.is_active = False
            user.save()
            return redirect("/login.html")

        elif "save_changes" in request.POST:
            # Update the user's information using raw SQL query
            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_user SET username = %s, email = %s WHERE id = %s", [username, email, request.user.id])

            return redirect("/profile.html")

    return render(request, "home/profile.html")


@login_required
def view_challenges(request):
    user_id = request.user.id
    
    today = date.today()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = datetime.combine(today, datetime.max.time())

    # CALORIES
    # Get recipe completed by user
    with connection.cursor() as cursor:
        cursor.execute("SELECT RecipeID FROM userrecipe WHERE UserID = %s AND Datetime >= %s AND Datetime <= %s", [user_id, start_of_today, end_of_today])
        user_recipe_data = cursor.fetchall()

    recipe_ids = [recipe_data[0] for recipe_data in user_recipe_data]

    nutrition_data = nutrition_collection.find({'RecipeID': {'$in': recipe_ids}})

    # Calculate calories
    nutrition_facts = []
    total_calories = 0
    for nutrition_fact in nutrition_data:
        serving_size = nutrition_fact['Servings']
        nutrition_fact['CaloriesPerServing'] = round(nutrition_fact['Calories'] / serving_size, 2)
        nutrition_facts.append(nutrition_fact)
        total_calories += nutrition_fact['CaloriesPerServing']
    
    daily_calories_limit = 2000
    # remaining_calories = daily_calories_limit - total_calories not needed
    total_calories_percentage = (total_calories / daily_calories_limit) * 100

    total_calories = round(total_calories,2)        
    # remaining_calories = round(remaining_calories,2) not neeeded
    total_calories_percentage = round(total_calories_percentage)

    if total_calories_percentage < 100:
        calorie_status = "In Progress"
    else:
        total_calories_percentage = 100
        calorie_status = "Completed"

    # COUNT 
    #get count of number of recipes completed by user
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(RecipeID) FROM userrecipe WHERE UserID = %s AND Datetime >= %s AND Datetime <= %s", [user_id, start_of_today, end_of_today])
        user_recipe_count = cursor.fetchone()[0]

    # count resets daily with challenge basis
    recipe_count_number = 3

    if user_recipe_count < recipe_count_number:
        count_status = "In Progress"
        total_count_percentage = (user_recipe_count / recipe_count_number) * 100
        total_count_percentage = round(total_count_percentage)
    else:
        count_status = "Completed"
        total_count_percentage = 100
    


    # INGREDIENTS
    ingredient_array = ['Onion', 'Chicken', 'Salmon', 'Soy Sauce', 'Rice', 'Sugar', 'Salt']
    current_day = datetime.now().weekday() # return int which can be referenced to the index of the array above

    ingredient_of_the_day = ingredient_array[current_day]

    # get ingredient name from user > recipe > ingredients
    query = '''
        SELECT i.Name
        FROM auth_user u 
        JOIN userrecipe ur ON u.id = ur.UserID 
        JOIN recipe r ON ur.RecipeID = r.RecipeID 
        JOIN recipeingredient ri ON r.RecipeID = ri.RecipeID 
        JOIN ingredient i ON ri.IngredientID = i.IngredientID 
        WHERE u.id = %s AND Datetime >= %s AND Datetime <= %s
    '''
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id, start_of_today, end_of_today])
        result = cursor.fetchall()

    user_ingredients = [row[0].lower() for row in result]

    ingredient_status = 'In Progress'
    ingredient_count = 0

    for user_ingredient in user_ingredients:
        if user_ingredient == ingredient_of_the_day.lower():
            ingredient_status = 'Completed'
            ingredient_count += 1
            break
    
    ingredient_count_percentage = (ingredient_count / 1) * 100
    ingredient_count_percentage = round(ingredient_count_percentage)

    # calculate percentage for progress bar
    total_percentage = ((total_calories_percentage + total_count_percentage + ingredient_count_percentage) / 300 )*100
    total_percentage = round(total_percentage)

    context = {
        'total_calories': total_calories,
        # 'remaining_calories': remaining_calories, not needed
        'daily_calories_limit': daily_calories_limit,
        'total_calories_percentage': total_calories_percentage,
        'calorie_status': calorie_status,
        'count_status': count_status,
        'user_recipe_count':user_recipe_count,
        'recipe_count_number': recipe_count_number,
        'total_count_percentage': total_count_percentage,
        'ingredient_of_the_day':ingredient_of_the_day,
        'user_ingredients':user_ingredients,
        'ingredient_status':ingredient_status,
        'ingredient_count':ingredient_count,
        'ingredient_count_percentage':ingredient_count_percentage,
        'total_percentage':total_percentage,
        'segment'  : 'challenges'
    }
    
    return render(request, 'home/challenges.html', context)

@login_required
def view_profile(request):
    # Get the user's ID
    user_id = request.user.id
    

    # Query the 'Reviews' collection for reviews by UserID within the 'Reviews' array
    reviews_data = reviews_collection.find({'Reviews.UserID': user_id})
    
    # Process the retrieved reviews into a list
    reviews = []
    for review_data in reviews_data:
        for review in review_data['Reviews']:
            if review['UserID'] == user_id:
                recipe_id = review_data['RecipeID']
                
                file_document = fs.find_one({'reviewID': review['ReviewID']})
                file_data = {}
                if file_document:
                    file_data['content_type'] = file_document.content_type 
                    
                # Retrieve the Recipe.Name from the recipe table based on RecipeID
                with connection.cursor() as cursor:
                    cursor.execute("SELECT Name FROM recipe WHERE RecipeID = %s", [recipe_id])
                    recipe_data = cursor.fetchone()
                
                review_item = {
                    'ReviewID': review['ReviewID'],
                    'Name': review['Name'],
                    'Rating': review['Rating'],
                    'Text': review['Text'],
                    'UserID': review['UserID'],
                    'RecipeID': recipe_id,
                    'RecipeName': recipe_data[0] if recipe_data else None,
                    'FileData' : file_data
                }
                reviews.append(review_item)


    # Execute a raw SQL query to retrieve all dietary restrictions
    with connection.cursor() as cursor:
        cursor.execute("SELECT Name FROM dietrestriction")
        diet_restrictions_data = cursor.fetchall()

    # Process the retrieved dietary restrictions into a list
    diet_restrictions = [restriction_data[0] for restriction_data in diet_restrictions_data]
    
    # Execute a raw SQL query to retrieve the user's dietary restrictions with their names
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT dr.Name "
            "FROM dietrestriction AS dr "
            "INNER JOIN userdietrestriction AS udr ON dr.RestrictionID = udr.RestrictionID "
            "WHERE udr.UserID = %s",
            [user_id]
        )
        user_restrictions_data = cursor.fetchall()
    # Process the retrieved user's dietary restrictions into a list
    user_restrictions = [restriction_data[0] for restriction_data in user_restrictions_data]

    today = date.today()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = datetime.combine(today, datetime.max.time())
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT RecipeID, Name FROM recipe")
        recipe_data = cursor.fetchall()
        recipe_mapping = {recipe[0]: recipe[1] for recipe in recipe_data}
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT RecipeID FROM userrecipe WHERE UserID = %s AND Datetime >= %s AND Datetime <= %s", [user_id, start_of_today, end_of_today])
        user_recipe_data = cursor.fetchall()
        user_recipes = [{'RecipeID': recipe_data[0], 'RecipeName': recipe_mapping.get(recipe_data[0])} for recipe_data in user_recipe_data]

    # Get the list of RecipeIDs
    recipe_ids = [recipe_data[0] for recipe_data in user_recipe_data]

    # Query MongoDB collection for the RecipeIDs
    nutrition_data = nutrition_collection.find({'RecipeID': {'$in': recipe_ids}})

    print(recipe_ids)
    nutrition_facts = []
    total_calories = 0
    for nutrition_fact in nutrition_data:
        calculated_data = {
            'RecipeID' : nutrition_fact['RecipeID']
        }
        serving_size = nutrition_fact['Servings']
        calculated_data['CaloriesPerServing'] = round(nutrition_fact['Calories'] / serving_size, 2)
        calculated_data['ProteinPerServing'] = round(nutrition_fact['Protein'] / serving_size, 2)
        calculated_data['CarbohydratesPerServing'] = round(nutrition_fact['Carbohydrates'] / serving_size, 2)
        calculated_data['FatPerServing'] = round(nutrition_fact['Saturated_Fats'] / serving_size, 2)
        nutrition_facts.append(calculated_data)
        for _ in range(recipe_ids.count(nutrition_fact['RecipeID'])):
            total_calories += calculated_data['CaloriesPerServing']

    # Calculate remaining calories
    daily_calories_limit = 2000
    remaining_calories = daily_calories_limit - total_calories
    print(remaining_calories)
    #this is to check, if calories more than 0 then reccommend if not then dont!
    if remaining_calories > 0:
        recommended_recipes = nutrition_collection.aggregate([
            {'$match': {
                '$expr': {
                    '$lte': [{'$divide': ['$Calories', '$Servings']}, remaining_calories]
                },
                'Servings': {'$ne': 0}  
            }},
            {'$sample': {'size': 3}} 
        ])

        recommended_recipes_list = []
        for recipe in recommended_recipes:
            recipe_id = recipe['RecipeID']
            recipe_name = recipe_mapping.get(recipe_id)
            if recipe_name:
                recipe['RecipeName'] = recipe_name
                recommended_recipes_list.append(recipe)
    else:
        recommended_recipes_list = []
            
    total_calories = round(total_calories,2)        
    remaining_calories = round(remaining_calories,2)


    context = {
        'reviews': reviews,
        'diet_restrictions': diet_restrictions,
        'user_restrictions': user_restrictions,
        'selected_diet_restrictions': user_restrictions,  
        'nutrition_facts': nutrition_facts,
        'user_recipes': user_recipes,
        'total_calories': total_calories,
        'remaining_calories': remaining_calories,
        'recommended_recipes': recommended_recipes_list,
        'daily_calories_limit': daily_calories_limit,
        'segment'  : 'profile'
    }
    
    return render(request, 'home/profile.html', context)

@login_required(login_url="/login/")
def update_review(request, review_id):
    if request.method == 'POST':
        rating = request.POST['rating']
        text = request.POST['text']
        
        # Update the review in the MongoDB collection
        reviews_collection.update_one(
            {'Reviews.ReviewID': review_id},
            {'$set': {'Reviews.$.Rating': rating, 'Reviews.$.Text': text}}
        )
        
        return redirect('/profile.html')  # Redirect to the profile page
        
    return redirect('home')  # Handle non-POST requests by redirecting to home page

@login_required(login_url="/login/")
def delete_review(request, review_id):
    if request.method == 'GET':
        # Get document based on review_id
        document = reviews_collection.find_one(
            {"Reviews": {"$elemMatch": {"ReviewID": review_id}}})
        
        review_length = len(document['Reviews'])

        # Remove document if this is the only review in document
        if review_length == 1:
            reviews_collection.delete_one({"RecipeID": document['RecipeID']})

        # Update overall ratings and delete the review from the MongoDB collection
        else:
            reviews_collection.update_one(
                {"RecipeID": document['RecipeID']},
                  {'$pull': 
                    {'Reviews': 
                      {'ReviewID': review_id}
                    }
                  }
            )
            
            # Update overall rating
            reviews_collection.update_one(
                {'RecipeID': document['RecipeID']},  
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
        # Check if file exists for this review
        file_document = fs.find_one({ 'reviewID' : review_id })
        if file_document: 
            # Delete the file and their chunks
            fs.delete(file_document._id)
        return redirect('/profile.html')  
        
    return redirect('home')  

def update_restriction(request):
    user_id = request.user.id
    if request.method == 'POST':
        # Save the selected dietary restrictions for the user 
        selected_restrictions = request.POST.getlist("diet_restrictions")
        restriction_names = selected_restrictions[0].split(",")
        with connection.cursor() as cursor:
            # Delete existing dietary restrictions so that wont append causing duplicate records
            cursor.execute(
                "DELETE FROM userdietrestriction WHERE userid = %s",
                [user_id]
            )
            # Insert the selected dietary restrictions into the table 
            for restriction_name in restriction_names:
                cursor.execute(
                    "INSERT INTO userdietrestriction (userid, restrictionid) "
                    "SELECT %s, restrictionid FROM dietrestriction "
                    "WHERE name = %s",
                    [user_id, restriction_name]
                )

        return redirect('/profile.html')

@login_required
def get_file_data(request):
    if request.method == "POST":
        review_ids = request.POST.getlist('review_ids[]')
        file_data = {}

        for review_id in review_ids:
            file_document = fs.find_one({'reviewID': int(review_id)})
            file_data[review_id] = {
                'mime_type' : file_document.mime_type ,
                'file' :  base64.b64encode(file_document.read()).decode('ascii') 
            }

        # User hasn't made the recipe, show an error message
        json_response = json.dumps(file_data)
        # Redirect to the profile page or any other desired location
        return HttpResponse(json_response, content_type='application/json;charset=utf-8')

    return redirect('/profile.html')

@login_required
def remove_image(request, review_id):
    if request.method == "POST":
        # Get _id
        file_id = fs.find_one({ 'reviewID' : review_id })._id
        fs.delete(file_id)
        response = {
            'success' : True
        }
        # User hasn't made the recipe, show an error message
        json_response = json.dumps(response)
        # Redirect to the profile page or any other desired location
        return HttpResponse(json_response, content_type='application/json;charset=utf-8')

    return redirect('/profile.html')