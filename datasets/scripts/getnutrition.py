"""
calculate and update nutrition values for food.com
"""
import pymongo
import pandas as pd

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
newdb = myclient['INF2005_DB']
recipecol = mydb["recipe"]
newcol = newdb['Nutrition']
servingscol = mydb['food.com']

df = pd.read_csv("RAW_recipes.csv", usecols = ['id', 'name', 'nutrition'])

i=0
for doc in recipecol.find( {"source" : "food.com"}):

    newdoc = {"RecipeID" : doc['recipeid']}
    nutrition = df.loc[df['id'] == int(doc['id'])].iloc[0]['nutrition']

    nutrition = nutrition.strip('][')

    nutrition = nutrition.split(",")
    newdoc['Servings'] = servingscol.find_one({'id' : doc['id']})['Servings']
    newdoc['Calories'] = round(float(nutrition[0]), 2)
    newdoc['Total_Fats'] = round((65.0 * float(nutrition[1]) /100), 2)
    newdoc['Sugars'] = round((25.0 * float(nutrition[2]) /100), 2)
    newdoc['Sodium'] =  round((2.4 * float(nutrition[3]) /100), 2)
    newdoc['Protein'] = round((50.0 * float(nutrition[4]) /100), 2)
    newdoc['Saturated_Fats'] = round((20.0 * float(nutrition[5]) /100), 2)
    newdoc['Carbohydrates'] = round((300.0 * float(nutrition[6]) /100), 2)

    i+= 1
    print(i)
    newcol.insert_one(newdoc)

    
    


        