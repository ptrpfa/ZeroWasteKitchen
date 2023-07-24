"""
collate data for sql recipe table
"""
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
newcol = mydb["sqldata"]
recipecol = mydb['recipe']
yummlycol = mydb['main']
foodcol = mydb['food.comattributes']


c = 0
#food.com
for doc in foodcol.find():
    recipeid = recipecol.find_one({"id" : doc['id']})['recipeid']
    newData = {"RecipeID" : recipeid}
    newData['Name'] = doc['name']
    newData['Description'] = doc['description']
    newData['Cuisine'] = doc['cuisine']
    newData['MealType'] = doc['mealType']

    newcol.insert_one(newData)
    c += 1
    print(c)

for doc in yummlycol.find():

    recipeid = recipecol.find_one({"id" : doc['id']})['recipeid']
    newData = {"RecipeID" : recipeid}
    newData['Name'] = doc['name']
    newData['Description'] = doc['description']
    newData['Cuisine'] = doc['cuisine']
    newData['MealType'] = doc['mealType']
    newcol.insert_one(newData)
    c += 1
    print(c)

