#!/usr/bin/env python3

from twython import Twython, TwythonStreamer
from pprint import PrettyPrinter

class Streamer(TwythonStreamer):

    def on_success(self, data):

        if data['user']['id_str'] != TRUMP_ID:
            return

        pp = PrettyPrinter()
        print(pp.pprint(data))

        if 'text' in data:
            print(data['text'])

    def on_error(self, status_code, data):
        print(status_code)

APP_KEY       = '3YkdRq6EcjZZP52H2G1Xr7USq'
APP_SECRET    = 'nubk75G1LBwg2uZI5CUK2fVrnG91BF94rcCAFgL0Rj7DKBufzO'
ACCESS_KEY    = '1190403948156477440-QW3dvfPd2722VdEd3cA683DewpZEB1'
ACCESS_SECRET = 'O11jWcr8Zb7ATgAtbi8PIGkF24CwmNsyCClMKI1LAMfnR'
TRUMP_ID      = '25073877'

pp = PrettyPrinter()
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
twitter = Twython(APP_KEY, access_token=twitter.obtain_access_token())

timeline = twitter.get_user_timeline(screen_name='realDonaldTrump', count=1, tweet_mode='extended')
pp.pprint(timeline[0]) #['full_text'])

stream = Streamer(APP_KEY, APP_SECRET,
                  ACCESS_KEY, ACCESS_SECRET)

stream.statuses.filter(follow=[TRUMP_ID])
