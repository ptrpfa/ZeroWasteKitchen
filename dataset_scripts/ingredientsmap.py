"""
recipeid to ingredientid mapping 
"""
import pandas as pd
import json, csv
df= pd.read_csv("new_ingredients.csv")

print(df)


with open("ingredients.json", encoding="utf-8") as json_file:
    json_text = json.load(json_file)


with open('ingredientmap.csv', 'a', newline='') as f:
    for recipe in json_text:
        for ingredient in recipe['Ingredients']:
            row = df.loc[df['Name'] == ingredient].iloc[0]
            newrow = {"RecipeID" : recipe['RecipeID'], "IngredientID": row['IngredientID']}
            writer = csv.DictWriter(f, fieldnames=newrow.keys())
            # Append single row to CSV
            writer.writerow(newrow)
        print(recipe['RecipeID'])


