### INF2003 Database Systems Group 9: Zero Waste Kitchen
2200692 Pang Zi Jian Adrian <br>
2200959 Peter Febrianto Afandy <br>
2201014 Tng Jian Rong <br>
2201132 Lionel Sim Wei Xian <br>
2201159 Ryan Lai Wei Shao
### Project Overview
The "Zero Waste Kitchen" (ZWK) project aims to address the ongoing issue of household food wastage by providing users with a practical tool that empowers them to make efficient use of their kitchen ingredients, thereby reducing food waste. By offering personalized recipe recommendations collected and refined from large datasets like Yummy.com and Food.com, the ZWK project aims to encourage users to utilize their available ingredients more effectively. The project is implemented using a user-friendly web application, to provide convenience and quick access to users. 
![ZWK](docs/ZWK.png)
By leveraging on database technologies and advanced queries, the application offers users a seamless experience to input their available ingredients and receive tailored recipe suggestions instantly. For further recipe refinements, the application supports a suite of advanced filtering options, such as by dietary restrictions and number of ingredients. This provides users with creative and exciting ways to utilise their existing ingredients, thereby promoting sustainable and mindful cooking practices. To encourage the platform’s usage amongst users, ZWK also allows users to track recipes that they have cooked, participate in recipe challenges, leave recipe reviews, and engage with a community of likeminded food enthusiasts.

### System Architecture
<u>Overview</u><br>
The ZWK project consists of a Django-based web application that serves as the primary interface for users to interact with the application, as well as a MySQL, MongoDB, and Redis database. The project builds on top of an existing Django template, Argon, to speed up development and focus the team’s efforts onto database operations. It is important to note that all SQL queries performed on the web application are implemented using raw SQL, even though Django provides its own ORM-model for queries. 

![System Architecture](docs/arch.png)

<u>Relational Database</u><br>
The MySQL relational database is used as the application’s main database to store atomic data, to allow for the correlation of information from its tables and the MongoDB collections. It includes tables such as Recipe, Dietary Restriction, Ingredient and User, as well as junction tables to represent the relationships between these tables after performing database normalisation on many-to-many relationships. 

![ERD](docs/erd.png)

<u>Non-Relational Database (MongoDB)</u><br>
A document-based MongoDB database is used for the ZWK application to store unstructured information that are diverse in nature, due to differences in the datasets obtained. It consists of three data collections, Recipe Instructions, Recipe Reviews and Recipe Nutrition. These data are selected to be stored in a document-based non-relational database due to their unstructured and diverse nature, and to provide scalability for future data additions. 

![MongoDB](docs/mongo.png)

<u>Non-Relational Database (Redis)</u><br>
A key-value-based Redis non-relational database is used for caching. The Redis database is used to optimize the performance of recipe queries made by users, by saving the results of search queries and the search options entered. If the same search query and options are entered by a user, the ZWK application will fetch the results of the query from the Redis cache database, instead of querying the SQL database. The Redis database provides improved efficiency by enabling faster retrieval of previously accessed recipes, which is especially useful for popular searches.

![MongoDB](docs/redis.png)

### Submission Files
```
README.md (this file)

docs/ (images for documenttion)

datasets/ (processed datasets obtained from the various data sources)

nosql/ (import files for the non-relational database)

sql/ (import files for the relational database)

web/ (main web application platform to deploy the ZWK project)

```
### Project Installation Instructions
---
The `web/` folder contains the main source code used to deploy the Zero Waste Kitchen application. Our application runs on Django, a Python-based web framework. Please ensure that your computing environment has Python installed. To run the application, follow the instructions below.

1. Change your current directory to the `web/` folder:
    ```
    cd web
    ```
2. Create a Python virtualenv on your local environment:
    ```
    python3 -m venv .venv
    ```

3. Activate your created virtualenv:
    ```
    source .venv/bin/activate
    ```

4. Download the application's required dependencies and libaries:
    ```
    pip3 install -r requirements.txt
    ```

5. Create a copy of the `.env_prod` file to `.env`, and update your settings (if any). It is recommended for you to connect to our **Cloud** databases as they have already been pre-configured for use. However, if you plan on setting up your own MySQL, MongoDB and Redis database servers, ensure that you have changed the connection details in your `.env` file! More instructions on how to set up and import the various datasets to your three local databases can be found [here](#full-database-setup).
    ```
    cp .env_prod .env
    ```

6. Run the Django web application (default port 8000)!
    ```
    python3 argon/manage.py runserver
    ```

    If you are using our Cloud databases, you can login using the following credentials:
    ```
    Username: test
    Password: test
    ```

    Otherwise, you can choose to login using Google SSO, or just register a new account to get started!

### Full Database Setup
something here
```
python3 argon/manage.py makemigrations
python3 argon/manage.py migrate
```