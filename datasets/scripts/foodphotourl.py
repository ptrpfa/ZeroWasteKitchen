"""
scrape image url from food.com
"""
from recipe_scrapers import scrape_me
import pandas as pd
import pymongo

TOTAL = 43028

# read csv file 
df = pd.read_csv("RAW_recipes.csv", usecols = ['name','id'])

# connect to db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["recipe"]


i = TOTAL - len(list(mycol.find({"image_url" : {"$exists" : True}})))
    
for doc in mycol.find({ "$and": [ { "source": "food.com" }, { "image_url": {"$exists" : False}}]}):

    row = df.loc[df['id'] == int(doc['id'])].iloc[0]

    recipeid = str(row["id"])
    string = str(row["name"])
    link = "https://www.food.com/recipe/" +'-'.join(string.split()) + "-" + recipeid
    try:
        scraper = scrape_me(link)
        # ignore default image
        if scraper.image() == 'https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/gk-static/fdc-new/img/fdc-shareGraphic.png':
            image_url = "noImage"
        else:
            image_url = scraper.image()
    except Exception as e:
        image_url = "noImage"

    mycol.update_one({"id": recipeid}, {"$set": {"image_url": image_url}})
    i -= 1
    print(i, recipeid)


