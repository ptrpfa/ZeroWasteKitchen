"""
create Instructions collection for nosql
"""
import os, json
import pymongo
import pandas as pd


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
olddb = myclient["Local"]
newdb = myclient['INF2005_DB']
newcol = newdb['Instructions']
recipecol = olddb["recipe"]
foodcol = olddb['food.com']

path_to_json_files = './recipes'
df = pd.read_csv("RAW_recipes.csv", usecols = ['id', 'minutes'])

# yummly
x=0
for doc in recipecol.find({"source" : "yummly"}):
    newDocument = {}
    currid = doc['id']
    

    newDocument['RecipeID'] = doc['recipeid']
    newDocument['Steps'] = len(doc['recipe'])
    with open(os.path.join(path_to_json_files, currid + '.json')) as json_file:
        json_text = json.load(json_file)


    instructions = []
    for i, step in enumerate(doc['recipe']):
        instructions.append( {'Description' : step })
    newDocument['Instructions'] = instructions
    newDocument['Ingredient_Lines'] = json_text['ingredientLines']
    newDocument['Total_Time'] = 5 * round(json_text['totalTimeInSeconds']/300)

    
    newcol.insert_one(newDocument)
    x += 1
    print(x)


#food.com
for doc in recipecol.find({"source" : "food.com"}):
    newDocument = {}
    currid = doc['id']
    newDocument['RecipeID'] = doc['recipeid']
    newDocument['Steps'] = len(doc['recipe'])
    instructions = []
    for i, step in enumerate(doc['recipe']):
        instructions.append( {'Description' : step })
    newDocument['Instructions'] = instructions
    newDocument['Ingredient_Lines'] = foodcol.find_one({"id" : currid})['ingredientsline']
    newDocument['Total_Time'] = int(df.loc[df['id'] == int(currid)].iloc[0]['minutes'])
    
    print(x)
    newcol.insert_one(newDocument)
    x += 1