"""
update cuisine, mealtype for yummly data
"""
import os, json
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["recipe"]

newcol = mydb['main']

path_to_json_files = './lists'
json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]

i = 0

attributedata = {}
namedata = {}
while i != 19:
    with open(os.path.join(path_to_json_files, json_file_names[i])) as json_file:
        json_text = json.load(json_file)
        for x in json_text["matches"]:
            attributedata[x['id']] = x['attributes']
            namedata[x['id']] = x['recipeName']
    i += 1

cuisine = ['American', 'Chinese', 'Thai',  'Greek', 'Mexican', 'Italian', 'Indian', 'English', 'Hawaiian', 'Spanish', 'Mediterranean', 'Moroccan', 'French', 'German', 'Japanese', 'Hungarian', 'Irish', 'Portuguese', 'Cuban', 'Swedish',  'Filipino', 'Brazilian', 'Vietnamese', 'Turkish', 'Jamaican', 'Korean', 'Southwestern', 'Cajun & Creole', 'Southern & Soul Food', 'Kid-Friendly', 'Asian', 'Barbecue']
course = ['Main Dishes', 'Soups', 'Lunch', 'Salads', 'Breads', 'Side Dishes', 'Appetizers', 'Condiments and Sauces', 'Breakfast and Brunch', 'Desserts', 'Snacks']

for doc in mycol.find():
    
    currid = doc['id']
    newdata = {'id' : currid, "source" : "yummly"}

    for a in cuisine:
        if a in attributedata[currid]['cuisine']:
            newdata['cuisine'] = a
            break
    for b in course:
        if b in attributedata[currid]['course']:
            newdata['mealType'] = b
            break
    newdata['name'] = namedata[currid]
    newdata['description'] = namedata[currid]
    
    newcol.insert_one(newdata)


