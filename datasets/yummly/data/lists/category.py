import json

ingredient_categories = {
    "seasoning": ["salt", "pepper", "spice"],
    "sweetener": ["sugar", "honey"],
    "baking": ["flour", "baking powder", "baking soda"],
    # Add more ingredient categories and keywords as needed
}

def classify_ingredients(ingredients):
    categorised_ingredients = {}
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        category = None
        for cat, keywords in ingredient_categories.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                category = cat
                break
        if category:
            if category in categorised_ingredients:
                categorised_ingredients[category].append(ingredient)
            else:
                categorised_ingredients[category] = [ingredient]
        else:
            categorised_ingredients["other"] = categorised_ingredients.get("other", []) + [ingredient]
    return categorised_ingredients

# Read JSON data from file (Change to ur file name)
with open("ingredient.json") as file:
    data = json.load(file)

# Extract the "matches" list from the loaded JSON data
matches = data.get("matches", [])

# Classify ingredients for each match
categorised_matches = []
for match in matches:
    ingredients = match.get("ingredients", [])
    categorised_ingredients = classify_ingredients(ingredients)
    categorised_match = {
        "recipeName": match.get("recipeName"),
        "categorisedIngredients": categorised_ingredients
    }
    categorised_matches.append(categorised_match)

# Stores categorised matches in anoter JSON file
with open("categorised_ingredients.json", "w") as file:
    json.dump(categorised_matches, file)

# Print the categorised ingredients
for categorised_match in categorised_matches:
    recipe_name = categorised_match["recipeName"]
    categorised_ingredients = categorised_match["categorisedIngredients"]
    print(f"Recipe: {recipe_name}")
    for category, ingredients in categorised_ingredients.items():
        print(f"{category.capitalize()}:")
        print(ingredients)
    print()
