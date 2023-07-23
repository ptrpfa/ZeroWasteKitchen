from unidecode import unidecode
import pandas as pd

# CSV file path
CSV_FILE_INGREDIENTS = 'categorised_ingredients.csv'
CSV_FILE_RECIPE_INGREDIENT = 'ingredientmap.csv'

#reading the csv
ingredients = pd.read_csv(CSV_FILE_INGREDIENTS)   
recipeingredient = pd.read_csv(CSV_FILE_RECIPE_INGREDIENT)  

# Create a new column for decoded names
ingredients['Decoded_Name'] = ingredients['Name'].apply(lambda x: unidecode(x))

# Check for duplicate names
duplicate_names = ingredients[ingredients['Decoded_Name'].duplicated(keep=False)]

# Drop duplicates based on the decoded names, keeping the first occurrence
unique_ingredients = ingredients.drop_duplicates(subset='Decoded_Name', keep='first').copy()

# Change the "Name" column value to "Decoded_Name" value
unique_ingredients['Name'] = unique_ingredients['Decoded_Name']

# Replace the "IngredientID" column with the DataFrame index
unique_ingredients['IngredientID'] = unique_ingredients.reset_index().index

# Create a dictionary to map IngredientID based on name similarity
dup_mapping_dict = {}

for _, row in duplicate_names.iterrows():
    name = row['Decoded_Name']
    ingredient_id = row['IngredientID']
    first_occurrence_id = duplicate_names[duplicate_names['Decoded_Name'] == name]['IngredientID'].iloc[0]
    if first_occurrence_id != ingredient_id:
        dup_mapping_dict[ingredient_id] = unique_ingredients.loc[unique_ingredients['Name'] == name, 'IngredientID'].iloc[0]


# Update the IngredientID in recipeingredient dataset
# Replace all the key value found in the recipeingredient to the value of the pair
# Get the second duplicated ID, replace it with the first occurence ID
recipeingredient['IngredientID'] = recipeingredient['IngredientID'].replace(dup_mapping_dict)

# Prepare to update csv

# Remove the extra column
unique_ingredients = unique_ingredients.drop('Decoded_Name', axis=1)

# Update the CSV_FILE_INGREDIENTS with unique_ingredients dataset
unique_ingredients.to_csv(CSV_FILE_INGREDIENTS, index=False)

# Update the CSV_FILE_RECIPE_INGREDIENT with the updated recipeingredient dataset
recipeingredient.to_csv(CSV_FILE_RECIPE_INGREDIENT, index=False)



