from TwitterAPI import TwitterAPI
import json
import os

consumer = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access = os.environ['ACCESS_TOKEN']
secret = os.environ['SECRET_TOKEN']
api = TwitterAPI(consumer, consumer_secret, access, secret)

r = api.request("direct_messages/events/list")
print(r.text)
