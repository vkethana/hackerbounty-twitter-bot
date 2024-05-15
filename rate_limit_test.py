import tweepy
import os
import logging
logging.basicConfig(level=logging.DEBUG)

secrets = {}
secrets['consumer_key'] = os.environ['consumer_key']
secrets['consumer_secret'] = os.environ['consumer_secret']
secrets['access_token'] = os.environ['access_token']
secrets['access_token_secret'] = os.environ['access_token_secret']
secrets['bearer_token']=os.environ['bearer_token']
client = tweepy.Client(
		consumer_key = secrets['consumer_key'],
		consumer_secret = secrets['consumer_secret'],
		access_token = secrets['access_token'],
		access_token_secret = secrets['access_token_secret'],
		bearer_token=secrets['bearer_token']
)
resp = client.create_tweet(text="rate limit test")
