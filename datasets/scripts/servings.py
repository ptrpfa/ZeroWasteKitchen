"""
scrape servings from food.com
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pymongo
import pandas as pd
import os

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["food.com"]
df = pd.read_csv("RAW_recipes.csv", usecols = ['name','id'])

ids = []

for doc in mycol.find({"Servings" : {"$exists" : False}}):
    ids.append(int(doc['id']))
    
counter = len(ids)

for i in ids:
    data = {}
    row = df.loc[df['id'] == int(i)].iloc[0]

    recipeid = str(row["id"])
    string = str(row["name"])
    link = "https://www.food.com/recipe/" +'-'.join(string.split()) + "-" + recipeid

    options = webdriver.ChromeOptions() 
    driver = uc.Chrome(options=options)
    driver.get(link)

    try:
        btn = driver.find_element(By.CLASS_NAME, "facts__nutrition")
        btn.click()
        txt = driver.find_elements(By.CLASS_NAME, "svelte-epeb0m")
        servings = txt[8].text.split()[-1]
        query = {'id' : str(i)}
        newvalue = { "$set": { "Servings": int(servings) } }
        mycol.update_one(query, newvalue)
    except Exception as e:
        print(e)
        print("Exception occured")
    finally:
        driver.quit()
        os.system("taskkill /f /im chrome.exe /T")   

    counter -= 1
    print(counter, recipeid, servings)








 