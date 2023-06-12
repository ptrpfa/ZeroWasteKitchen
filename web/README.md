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
    pip3 install -r argon/requirements.txt
    python3 argon/manage.py makemigrations
    python3 argon/manage.py migrate
    ```

4. Run Djagon web app (default port 8000)
    ```
    python3 argon/manage.py runserver
    ```

5. Default credentials (temporart)
    ```
    Username: test
    Password: test
    ```