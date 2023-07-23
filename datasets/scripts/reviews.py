"""
import reviews into mongo
"""
import pymongo
import pandas as pd

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
newdb = myclient['INF2005_DB']
mycol = mydb["recipe"]
newcol = newdb['Reviews']

df = pd.read_csv("RAW_interactions.csv", usecols = ['recipe_id', 'rating','review'])

#food.com

i = 0

for doc in mycol.find({"source" : "food.com"}):
    currid = int(doc['id'])
    rows = df.loc[df['recipe_id'] == currid]

    if not rows.empty:
        recipeid = doc['recipeid']
        newdoc = { "RecipeID" : recipeid}
        
        reviews = []
        overall = 0
        c = 1
        for x in range(len(rows.index)):
            reviewid = int(str(recipeid) + f"{c:03}")
            item = rows.iloc[x]
            review_text = str(item['review']).replace('&#039;', "'").replace('&lt;br/&gt;', '\n').replace("<br>", "\n")
            review = {'ReviewID' : reviewid ,'Name' : "Anonymous", "Rating" : int(item['rating']), "Text" : review_text, "UserID" : 0}
            overall += int(item['rating'])
            reviews.append(review)
            c += 1
        overall = overall/c
        overall = round(overall*2)/2
        newdoc['Overall_rating'] = overall
        newdoc['Reviews'] = reviews
        newcol.insert_one(newdoc)
    i += 1
    print(i)

#yummly
for doc in mycol.find({"source" : "yummly"}):
    if doc['status'] == "available":
        recipeid = doc['recipeid']
        newdoc = { "RecipeID" : recipeid}
        reviews = []
        c = 1
        overall = 0.0
        for item in doc['reviews']:
            reviewid = int(str(recipeid) + f"{c:03}")
            review_text = str(item['text']).replace('&#039;', "'").replace('&lt;br/&gt;', '\n').replace("<br>", "\n")
            review = {'ReviewID' : reviewid, 'Name' : item['name'], "Rating" : int(item['rating']), "Text" : review_text, "UserID" : 0}
            overall += int(item['rating'])
            reviews.append(review)
            c += 1
        overall = overall/c
        overall = round(overall*2)/2
        newdoc['Overall_rating'] = overall
        newdoc['Reviews'] = reviews
        newcol.insert_one(newdoc)
    i += 1
    print(i)

