# -*- encoding: utf-8 -*-

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from .models import Userdietrestriction, Dietrestriction
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


from core import settings


# Initialise global MongoDB connections
mongo_client, mongo_conn = settings.get_mongodb()
reviews_collection = mongo_conn['Reviews']



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

        # Update the user's information using raw SQL query
        with connection.cursor() as cursor:
            cursor.execute("UPDATE auth_user SET username = %s, email = %s WHERE id = %s", [username, email, request.user.id])

        # Redirect to the profile page or any other desired location
        return redirect("/profile.html")

    return render(request, "home/profile.html")

@login_required
def view_review(request):
    # Get the user's ID
    user_id = request.user.id
    # Query the 'Reviews' collection for reviews by UserID within the 'Reviews' array
    reviews_data = reviews_collection.find({'Reviews.UserID': user_id})
    # Process the retrieved reviews into a list
    reviews = []
    for review_data in reviews_data:
        for review in review_data['Reviews']:
            if review['UserID'] == user_id:
                review_item = {
                    'ReviewID': review['ReviewID'],
                    'Name': review['Name'],
                    'Rating': review['Rating'],
                    'Text': review['Text'],
                    'UserID': review['UserID'],
                    'RecipeID': review_data['RecipeID']
                }
                reviews.append(review_item)

    # Pass the reviews to the template context
    context = {
        'reviews': reviews
    }

    return render(request, "home/profile.html", context)

# tried to use raw but dont work.... dk why will firgure out
# @login_required(login_url="/login/")
# def update_review(request, review_id):
#     if request.method == 'POST':
#         rating = request.POST['rating']
#         text = request.POST['text']
#         query = "UPDATE Reviews SET Rating = %s, Text = %s WHERE ReviewID = %s"
#         reviews_collection.execute(query, (rating, text, review_id))
        
#     return redirect('/profile.html')  # Redirect to the profile page
        
    

# @login_required(login_url="/login/")
# def delete_review(request, review_id):
#     if request.method == 'GET':
       
#         query = "DELETE FROM Reviews WHERE ReviewID = %s"
#         reviews_collection.execute(query, (review_id,))
        
#     return redirect('/profile.html')  # Redirect to the profile page

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
        # Delete the review from the MongoDB collection
        reviews_collection.update_one(
            {'Reviews.ReviewID': review_id},
            {'$pull': {'Reviews': {'ReviewID': review_id}}}
        )
        
        return redirect('/profile.html')  # Redirect to the profile page
        
    return redirect('home')  # Handle non-GET requests by redirecting to home page
        
 






