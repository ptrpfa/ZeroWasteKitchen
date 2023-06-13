#! /bin/bash
# Simple bash script to migrate and create Django tables in default MySQL database
source ../.venv/bin/activate
python3 argon/manage.py makemigrations
python3 argon/manage.py migrate