"""
scrape photourl for yummly
"""
from recipe_scrapers import scrape_me
import pymongo
import json, os

TOTAL = 52965

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["recipe"]

data = {}

path_to_json_files = './recipes'

i = TOTAL - len(list(mycol.find({"image_url" : {"$exists" : True}})))

for doc in mycol.find({ "$and": [ { "source": "yummly" }, { "image_url": {"$exists" : False}}]}):
    currid = doc['id']
    with open(os.path.join(path_to_json_files, (currid   + ".json"))) as json_file:
        json_text = json.load(json_file)
        link = json_text["source"]["sourceRecipeUrl"]
        try:
            scraper = scrape_me(link, wild_mode=True)
            # food.com default image
            if scraper.image() == 'https://img.sndimg.com/food/image/upload/q_92,fl_progressive,w_1200,c_scale/v1/gk-static/fdc-new/img/fdc-shareGraphic.png':
                image_url = "noImage"
            else:
                image_url = scraper.image()
        except Exception as e:
            image_url = "noImage"

        mycol.update_one({"id": currid}, {"$set": {"image_url": image_url}})
        i -= 1
        print(i, currid)


