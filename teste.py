import os
import sys
import json
import time
import re
import psycopg2
import urlparse

from datetime import date, timedelta, datetime
import requests
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Text


# import atexit
#
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger
#
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
#     func=send_saving_notification,
#     trigger=IntervalTrigger(seconds=5),
#     id='savings_notification',
#     name='Sends savings notification',
#     replace_existing=True)
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
#
# def send_saving_notification():
#     print time.strftime("%A, %d. %B %Y %I:%M:%S %p")

DATABASES = {
    'default': {
        'NAME': 'messenger_bot',
        'USER': 'postgres',
        'PASSWORD': '14243160',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


Base = declarative_base()




try:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
except Exception as e:
    engine = create_engine('postgresql://'+DATABASES['default'].get('USER')+':'+ DATABASES['default'].get('PASSWORD') + '@'+DATABASES['default'].get('HOST')+':'+ DATABASES['default'].get('PORT') +'/'+ DATABASES['default'].get('NAME'))

else:
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
    engine = create_engine('postgresql://'+user+':'+ password + '@'+host+':'+ port +'/'+ database)




DATABASES = {
    'default': {
        'NAME': 'messenger_bot',
        'USER': 'postgres',
        'PASSWORD': '14243160',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

db = 'postgresql://'+DATABASES['default'].get('USER')+':'+ DATABASES['default'].get('PASSWORD') + '@'+DATABASES['default'].get('HOST')+':'+ DATABASES['default'].get('PORT') +'/'+ DATABASES['default'].get('NAME')

def __init__():
    dat = date.fromtimestamp(0)
    print(dat)
    print(db)

__init__()
