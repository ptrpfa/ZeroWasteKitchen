"""
upload recipes into mongo
"""
import pandas as pd
import pymongo

# read csv file 
df = pd.read_csv("RAW_recipes.csv", usecols = ['id', 'name', 'steps'])

# connect to db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
recipecol = mydb["recipe"]
mycol = mydb["food.com"]

i = 0
for doc in mycol.find():

    
    query = {'id' : str(doc['id'])}
    
    recipe = df.loc[df['id'] == int(doc['id'])].iloc[0]['steps']

    recipe = recipe.strip('][').replace('"' , "'")
    recipe = recipe.split("', '")
    recipe[0] = recipe[0][1:]
    recipe[-1] = recipe[-1][:-1]

    newvalue = { "$set": { "recipe": recipe } }
    recipecol.update_one(query, newvalue)
  
    i += 1
    print(i)



