# -*- encoding: utf-8 -*-

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.http import HttpResponse


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

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

# views.py
def recipe_detail_view(request, cuisine=None):
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
