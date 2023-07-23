"""
scrape recipe instructions and reviews from yummly source
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
from recipe_scrapers import scrape_me
import os, json
from selenium.common.exceptions import TimeoutException
import pymongo

START = 0
i = 0

path_to_json_files = './recipes'
json_file_names = [filename for filename in os.listdir(path_to_json_files) if filename.endswith('.json')]


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Local"]
mycol = mydb["recipe"]

for json_file_name in json_file_names:
    data = {}
    
    if i > START:
        success = False
        while not success:
            with open(os.path.join(path_to_json_files, json_file_name)) as json_file:
                json_text = json.load(json_file)
                
                data[json_text["id"]] = {}
                data[json_text["id"]]["id"] = json_text["id"]
                try:
                    # scrape recipe from source url, store as list
                    scraper = scrape_me(json_text["source"]["sourceRecipeUrl"], wild_mode=True)
                    recipe = scraper.instructions_list()
                except Exception as e:
                    recipe = []
                options = webdriver.ChromeOptions() 
                driver = uc.Chrome(options=options)
                driver.get(json_text["attribution"]["url"])
                
            print(i, json_text["name"])

            try:
                # no recipe
                if recipe == []:
                    data[json_text["id"]]["status"] = "unavailable"

                # website not available, recipe available
                elif ("404" in driver.title): 
                    data[json_text["id"]]["status"] = recipe
                
                # website available, recipe available
                else:
                    data[json_text["id"]]["recipe"] = recipe
                    exit = False
                    valid = False

                    # wait for website to load js
                    while not exit:
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "recipe-image"))
                            )
                            exit = True
                            valid = True
                        except TimeoutException:
                            driver.refresh()
                            time.sleep(2)
                            if ("404" in driver.title):
                                data[json_text["id"]]["status"] = "unavailable"
                                exit = True
                    if valid:
                        time.sleep(3)

                        # get reviews
                        wrapper = driver.find_element(By.ID, "reviews")
                        reviews = wrapper.find_elements(By.XPATH, "//div[@class='review media']")
                        if reviews:
                            data[json_text["id"]]["status"] = "available"
                            data[json_text["id"]]["reviews"] = []
                        
                            for review in reviews:
                                reviewinfo = {}
                                content = review.find_element(By.CLASS_NAME, "review-content")
                                reviewinfo["name"] = content.find_element(By.CSS_SELECTOR, "div.review-name>a:first-child").text

                                reviewinfo["rating"] = len(content.find_elements(By.CLASS_NAME, "full-star"))
                                reviewinfo["text"] = content.find_element(By.CLASS_NAME, "review-text").text
                                data[json_text["id"]]["reviews"].append(reviewinfo)
                        
                        # no reviews
                        else:
                            data[json_text["id"]]["status"] = "noReviews"
                
                # insert into db
                mycol.insert_one(data[json_text["id"]])
                success = True
            except Exception as e:
                print(e)
                print("Exception occured")
                print("Current i value: " + str (i))
                print("Current json_file_name: " + json_file_name)
                
            finally:
                driver.quit()
                os.system("taskkill /f /im chrome.exe /T")        
    i += 1
