import os

import psycopg2
from app import app

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Менять под глобальную базу данных
conn = psycopg2.connect(dbname='test_db', user='postgres', password='Qwerty7', host='localhost')
