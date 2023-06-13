import pymysql
import pandas as pd

# MySQL database configuration
DB_HOST = 'localhost'
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_NAME = 'recipedb'

# CSV file path
CSV_FILE = 'food.csv'
SQL_FILE = 'recipe_table_data.sql'

# Connect to the MySQL database
connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = connection.cursor()

#reading the csv
data = pd.read_csv (CSV_FILE)   
data = data.where((pd.notnull(data)), None)

for row in data.itertuples():
    recipe_id = int(row.recipeid)
    name = row.name
    description = row.description if pd.notnull(row.description) else ''
    cuisine = row.cuisine if pd.notnull(row.cuisine) else ''
    meal_type = row.mealType if pd.notnull(row.mealType) else 'General'

    cursor.execute(
        '''
        INSERT INTO recipe (RecipeID, Name, Description, Cuisine, MealType)
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (recipe_id, name, description, cuisine, meal_type)
    )

connection.commit()
connection.close()
print('CSV data inserted into MySQL table successfully.')
