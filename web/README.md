### Basic Setup
---
1. Create python virtualenv
    ```
    python3 -m venv .venv
    ```

2. Activate virtualenv
    ```
    source .venv/bin/activate
    ```

3. Download argon dependencies
    ```
    pip3 install -r requirements.txt
    python3 argon/manage.py makemigrations
    python3 argon/manage.py migrate
    ```

4. Create a copy of the `.env_prod` file to `.env`, and update settings (if any).
    ```
    cp .env_prod .env
    ```

5. Run Djagon web app (default port 8000)
    ```
    python3 argon/manage.py runserver
    ```

6. Default credentials (temporary)
    ```
    Username: test
    Password: test
    ```