"""
update cuisine and mealtype for food.com
"""
import pymongo
import pandas as pd

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["food.com"]
newcol = mydb['food.comattributes']

df_raw = pd.read_csv("RAW_recipes.csv")

cuisine = ['American', 'Chinese', 'Thai',  'Greek', 'Mexican', 'Italian', 'Indian', 'English', 'Hawaiian', 'Spanish', 'Mediterranean', 'Moroccan', 'French', 'German', 'Japanese', 'Hungarian', 'Irish', 'Portuguese', 'Cuban', 'Swedish',  'Filipino', 'Brazilian', 'Vietnamese', 'Turkish', 'Southwestern', 'Asian', 'Barbecue', 'North American', 'European', 'African', 'South American']
course = ['Main Dishes', 'Soups', 'Lunch', 'Salads', 'Breads', 'Side Dishes', 'Appetizers', 'Condiments and Sauces', 'Breakfast and Brunch', 'Desserts', 'Snacks', 'Beverages']

ids = []
for doc in mycol.find():
    ids.append(int(doc['id']))

counter = 0
for i in ids:
    newdata = {'id' : str(i)}
    row = df_raw.loc[df_raw['id'] == int(i)].iloc[0]
    res = row['tags'].strip('][').split(', ')
    for c in range(len(res)):
        res[c] = res[c][1:-1].replace("-", " ").replace("main dish", "main dishes").title().replace('Sauces', 'Condiments and Sauces').replace('Condiments Etc', 'Condiments and Sauces').replace('Soups Stews', 'Soups')
        if res[c] == "Breakfast" or res[c] == "Brunch":
            res[c] = 'Breakfast and Brunch'
    cuisineflag = False
    courseflag = False

    for cuisinetag in cuisine:
        if cuisinetag in res:
            cuisineflag = True
            newdata['cuisine'] = cuisinetag
            break
    
    for mealtypetag in course:
        if mealtypetag in res:
            courseflag = True
            newdata['mealType'] = mealtypetag
            break
      
    
    if not cuisineflag:
        newdata['cuisine'] = ""
    if not courseflag:
        newdata['mealType'] = ""
    
    newdata['name'] = mycol.find_one({'id': str(i)})['title']

    

    if not pd.isna(row['description']):
        newdata['description'] = row['description']
    else:
        newdata['description'] = newdata['name']
    newdata['source'] = "food.com"
    newcol.insert_one(newdata)
    counter += 1
    print(counter)








