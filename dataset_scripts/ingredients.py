"""
get raw ingredient list
"""

import json, csv

with open("ingredients.json", encoding="utf-8") as json_file:
    json_text = json.load(json_file)

ingredients = []
for recipe in json_text:
    for ingredient in recipe['Ingredients']:
        if ingredient not in ingredients:
            ingredients.append(ingredient)

        print(recipe['RecipeID'])


with open('new_ingredients.csv', 'w', newline='', encoding='utf-8') as f:
    # using csv.writer method from CSV package
    writer = csv.writer(f)
    # Append single row to CSV
    for ingredient in ingredients:
        writer.writerow([ingredient])