import pymysql
import pandas as pd
import csv 
import json
from fuzzywuzzy import fuzz

# MySQL database configuration
DB_HOST = 'localhost'
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_NAME = 'recipedb'
TABLE = 'dietrestriction'

# CSV file path
CSV_FILE = 'allergens.csv'
JSON_FILE = 'ingredients.json'
NEW_CSV = 'allergen_mapp.csv'

# Connect to the MySQL database
connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = connection.cursor()

# Get the allergens data frame
data = pd.read_csv(CSV_FILE, header=None, names=['Allergens']) 
data.index += 1 # increase index by 1
# Remove duplicates
data = data.drop_duplicates()

# for row in data.itertuples():
#     cursor.execute(
#         '''
#         INSERT INTO dietrestriction (RestrictionID, Name)
#         VALUES (%s, %s)
#         ''',
#         (row.Index, str(row.Allergens))
#     )

# read the json file 
with open(JSON_FILE, 'r') as file:
    json_data = json.load(file)


with open(NEW_CSV, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['RecipeID', 'AllergenIndex'])  # Write the header row

    matched_indices = set()

    start_index = 52965
    end_index = start_index + 3

    for i, recipe in enumerate(json_data[start_index:end_index], start=start_index):
        if i + 1 == end_index:
            break
        # result = pd.DataFrame(columns=['RecipeID', 'AllergenIndex'])

        # Clear the set for each recipe
        matched_indices.clear()
        # Prep for the SQL insertion
        batch_data = [] 

        # check the mapping for each ingredient 
        for ingredient in recipe['Ingredients']:
            fuzzy_matches = data[data['Allergens'].apply(lambda x: fuzz.partial_ratio(str(x).lower(), ingredient.lower())) > 90]

            if not fuzzy_matches.empty:
                # Add to the set
                matched_indices.update(fuzzy_matches.index)
                # for indice in list(fuzzy_matches.index):
                #     if(indice not in matched_indices):
                #         matched_indices.append(indice)

        for indice in matched_indices:
            # Write into csv for accounting
            writer.writerow([recipe['RecipeID'], indice])
            # Prepare the batch insert data for SQL
            batch_data.append((recipe['RecipeID'], indice))

        # Batch insert into the database
        cursor.executemany(
            '''
            INSERT INTO recipedietrestriction (RecipeID, RestrictionID)
            VALUES (%s, %s)
            ''',
            batch_data
        )
        connection.commit()

connection.close()
print('CSV data inserted into MySQL table successfully.')