import os

import psycopg2
from app import app

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Менять под глобальную базу данных
conn = psycopg2.connect(dbname='db0el5720jho8u', user='cartyygfeadefo', password='5210cc100165ec7e5ab2108e3f9930eeb1e0c011f0d8283e0f976d1dc640e511', host='ec2-52-45-83-163.compute-1.amazonaws.com')
