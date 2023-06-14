import pymysql
import pandas as pd

# MySQL database configuration
DB_HOST = '34.142.157.91'
DB_USER = 'root'
DB_PASSWORD = 'abangbongba'
DB_NAME = 'recipedb'

# CSV file path
CSV_FILE_INGREDIENTS = '../sql_datasets/categorised_ingredients.csv'
CSV_FILE_RECIPE_INGREDIENT = '../sql_datasets/ingredientmap.csv'

# Connect to the MySQL database
connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = connection.cursor()

#reading the csv
ingredients = pd.read_csv(CSV_FILE_INGREDIENTS)   
recipeingredient = pd.read_csv(CSV_FILE_RECIPE_INGREDIENT)  

for row in ingredients.itertuples():
    ingredient_id = int(row.IngredientID)
    name = row.Name
    category = row.Category

    print(ingredient_id)

    cursor.execute(
        '''
        INSERT INTO ingredient (IngredientID, Name, Category)
        VALUES (%s, %s, %s)
        ''',
        (ingredient_id, name, category)
    )
    connection.commit()

# print("Now Inserting Recipe Ingredient Mapping\n")

# for row in recipeingredient.itertuples():
#     ingredient_id = int(row.IngredientID)
#     recipe_id = int(row.RecipeID)

#     cursor.execute(
#         '''
#         INSERT INTO recipeingredient (RecipeID, IngredientID)
#         VALUES (%s, %s)
#         ''',
#         (recipe_id, ingredient_id)
#     )

#     connection.commit()

connection.close()
print('CSV data inserted into MySQL table successfully.')
