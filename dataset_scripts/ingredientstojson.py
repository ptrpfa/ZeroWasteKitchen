"""
get ingredient list for allergens mapping
"""
import os, json
import pymongo
import pandas as pd


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["Local"]
recipecol = db["recipe"]
newcol = db['ingredients_updated']

path_to_json_files = './lists'
json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

df = pd.read_csv("RAW_recipes.csv", usecols = ['id', 'ingredients'])


i = 0
jsonData = []
while i != 19:
    with open(os.path.join(path_to_json_files, json_file_names[i])) as json_file:
        json_text = json.load(json_file)
        for x in json_text['matches']:
            jsonData.append(x)
    i += 1

c = 0
for doc in recipecol.find({"source" : "yummly"}):
    
    currid = doc['id']
    newData = {"RecipeID" : doc['recipeid']}
    print(currid)
    found = False
    i = 0
    while not found:
        for x in jsonData:
            if x['id'] == currid:
                newData["Ingredients"] = x['ingredients']
                newcol.insert_one(newData)
                found = True
                c += 1
                print(c)
                break

#food.com
for doc in recipecol.find({"source" : "food.com"}):
    newDocument = {}
    currid = doc['id']
    newDocument['RecipeID'] = doc['recipeid']

    ingredients = df.loc[df['id'] == int(doc['id'])].iloc[0]['ingredients']
    ingredients = ingredients.strip('][').replace('"' , "'")
    ingredients = ingredients.split("', '")
    ingredients[0] = ingredients[0][1:]
    ingredients[-1] = ingredients[-1][:-1]

    newDocument['Ingredients'] = ingredients
    newcol.insert_one(newDocument)
    c += 1
    print(c)
