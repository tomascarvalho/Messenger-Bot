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
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Date, Float
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
    database=url.path[1:]
    user_name=url.username
    password=url.password
    host=url.hostname
    port=url.port
    engine = create_engine('postgresql://'+str(user_name)+':'+ str(password)+ '@'+str(host)+':'+ str(port) +'/'+ str(database))


Session = sessionmaker(bind=engine)
session = Session()
app = Flask(__name__)



class User_Session(Base):
    __tablename__ = 'user_session'
    id = Column(Integer, Sequence('user_id_seq'), primary_key = True)
    user_id = Column(String(60))
    date = Column(Date())
    amount = Column(Float())
    def __repr__(self):
        return "<User(user_id='%s')>" % (self.user_id)
    def get_date(self):
        return self.date

Base.metadata.create_all(engine)
session = Session()


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, get_reply(message_text, user_exists(sender_id), sender_id))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def get_reply(message_text, user, sender_id):

    if ("How much do I have saved?" in message_text or "How much" in message_text or "how much" in message_text or "When is my next saving day?" in message_text or "when is" in message_text):
        if (user == None): #The user is not yet in our DB
            new_user(sender_id)
            to_return = "When did you start saving and how much are you incrementing?\nPlease reply in the form dd/mm/yyyy x.xx"
            return to_return
        else:
            if (user.date == date.fromtimestamp(0)):
                to_return = "When did you start saving and how much are you incrementing?\nPlease reply in the form dd/mm/yyyy x.xx"
                return to_return
            else:
                return savings(user.date, user.amount)

    elif ("help" in message_text or "Help" in message_text):
        return "Hello, this is savings bot.\nThe idea is that you start by saving x euros and increment that amount every week.\nFor instance, if you start saving 1, after a week you have to save 2, and then 3 and by the end of the year you should have 1430.\nCommands for savings bot are: \"How much do I have saved?\"/\"When is my next saving day?\"/\"Help\""

    else:
        match = re.search(r'\d{2}/\d{2}/\d{4}', message_text)
        try:
            start_date = datetime.strptime(match.group(), '%d/%m/%Y').date()
        except Exception as e:
            return "Unknown command. Commands for savings bot are: \"How much do I have saved?\"/\"When is my next saving day?\"/\"Help\"\nIf you were inserting a date, make sure it's in the form dd/mm/yyyy"

        else:
            float_match = re.search(r'\d*\.\d{2}', message_text)
            try:
                amount = float(float_match.group())
            except Exception as e:
                return "You seem to have put the date, but forgot about the amount or the amount is in the wrong format. Please reply in the form dd/mm/yyyy x.xx"
            else:
                if (user == None):
                    new_user(sender_id)
                new_date_amount(user_exists(sender_id), start_date, amount)
                return savings(start_date, amount)

def savings(start_date, saving_amount):
    today = date.today()
    to_add = saving_amount
    saved = 0.00
    while (start_date < today):
        saved = saved + saving_amount
        saving_amount += to_add
        start_date = start_date + timedelta(days=7)

    return ("Your next saving day is: " +str(start_date)+ " and you have to save " + str(saving_amount)+ ".\nYou saved "+str(saved)+" until now.")



def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def user_exists(id):
    user = session.query(User_Session).filter(User_Session.user_id == id).first()
    return user

def new_user(id):
    dat = date.fromtimestamp(0)
    new_user = User_Session(user_id=id, date = date.fromtimestamp(0), amount = 0.00)
    try:
        session.add(new_user)
        session.commit()
    except Exception as e:
        log(e)
        log("error adding new_user")

def new_date_amount(user, new_dat, new_amount):
    user.date = new_dat
    user.amount = new_amount
    session.commit()

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
