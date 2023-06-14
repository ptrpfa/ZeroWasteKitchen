import pymysql
import pandas as pd

# MySQL database configuration
DB_HOST = '34.142.157.91'
DB_USER = 'root'
DB_PASSWORD = 'abangbongba'
DB_NAME = 'recipedb'
DB_TABLE = 'recipe'

# CSV file path
CSV_FILE = 'recipe.csv'
SQL_FILE = 'recipe_table_data.sql'


def check_recipe_exists(cursor, recipe_id):
    # Execute a SQL query to check if the recipe ID exists
    query = "SELECT RecipeID FROM recipe WHERE RecipeID = %s"
    cursor.execute(query, (recipe_id))

    # Fetch the first row (if any)
    row = cursor.fetchone()

    # Check if the recipe ID exists in the table
    if row is not None:
        return True
    else:
        return False

def update_or_insert_recipe(cursor, connection, recipe_id, name, description, cuisine, meal_type):
    if check_recipe_exists(cursor, recipe_id):
        # Recipe ID exists check if got duplicate 
        print("Updating RecipeId: ", recipe_id)
        update_query = "UPDATE recipe SET Name = %s, Description = %s, Cuisine = %s, Mealtype = %s WHERE RecipeID = %s"
        cursor.execute(update_query, ( name, description, cuisine, meal_type, recipe_id))
        connection.commit()
    else:
        # Recipe ID doesn't exist, perform insert
        print("Inserting RecipeId: ", recipe_id)
        insert_query = "INSERT INTO recipe (RecipeID, Name, Description, Cuisine, Mealtype) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, ( recipe_id, name, description, cuisine, meal_type))
        connection.commit()

# Connect to the MySQL database
try:
    connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    print("Connection successful!")

    cursor = connection.cursor()

    #reading the csv
    data = pd.read_csv (CSV_FILE)   
    data = data.where((pd.notnull(data)), None)

    for row in data.itertuples():
        recipe_id = int(row.RecipeID)
        name = row.Name
        description = row.Description if pd.notnull(row.Description) else ''
        cuisine = row.Cuisine if pd.notnull(row.Cuisine) else ''
        meal_type = row.Mealtype if pd.notnull(row.Mealtype) else 'General'
        update_or_insert_recipe(cursor, connection, recipe_id, name, description, cuisine, meal_type)

    connection.close()
    print('CSV data inserted into MySQL table successfully.')

except pymysql.Error as e:
    print("Connection failed:", e)



    # cursor.execute(
    #     '''
    #     INSERT INTO recipe (RecipeID, Name, Description, Cuisine, MealType)
    #     VALUES (%s, %s, %s, %s, %s)
    #     ''',
    #     (recipe_id, name, description, cuisine, meal_type)
    # )
    # connection.commit()


