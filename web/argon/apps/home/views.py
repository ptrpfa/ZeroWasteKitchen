# -*- encoding: utf-8 -*-
from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


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
