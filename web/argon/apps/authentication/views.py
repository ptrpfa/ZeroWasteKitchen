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

        # Update the user's information
        user = request.user
        user.username = username
        user.email = email
        user.save()

        # Redirect to the profile page or any other desired location
        return redirect("/profile.html")

    return render(request, "home/profile.html")



@login_required
def view_review(request):
    # Get the user's ID
    user_id = request.user.id

    # Execute a raw SQL query to retrieve reviews by UserID
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Reviews WHERE UserID = %s", [user_id])
        reviews_data = cursor.fetchall()

    # Process the retrieved reviews into a list
    reviews = []
    for review_data in reviews_data:
        review = {
            'ReviewID': review_data[0],
            'Name': review_data[1],
            'Rating': review_data[2],
            'Text': review_data[3],
            'UserID': review_data[4]
        }
        reviews.append(review)

    # Pass the reviews to the template context
    context = {
        'reviews': reviews
    }

    return render(request, 'home/profile.html', context)





