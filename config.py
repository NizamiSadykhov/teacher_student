import os

import psycopg2
from app import app

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Менять под глобальную базу данных
conn = psycopg2.connect(dbname='d9asfulh7bfmbd', user='rfmtowprcpllax', password='d630aac61a2f1304bc8d54bd3937cd8c6db1771eb5e51213ff59b05afd1277a3', host='ec2-52-204-196-4.compute-1.amazonaws.com')
