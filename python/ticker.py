#!/usr/bin/env python3

import os
import time
import pprint
import json
from queue import Queue
from threading import Thread
from datetime import datetime, tzinfo
from pytz import timezone
import epd2in7b
from PIL import Image, ImageDraw, ImageFont
from twython import Twython, TwythonStreamer


class Ticker(TwythonStreamer):

    TRUMP_ID      = '25073877'

    def __init__(self):

        with open('../keys.json') as f:
            KEYS = json.load(f)


        super(Ticker, self).__init__(
            KEYS['app_key'], KEYS['app_secret'], KEYS['access_key'], KEYS['access_secret'])

        self.pp    = pprint.PrettyPrinter()
        self.queue = Queue()
        self.epd   = epd2in7b.EPD()
        self.epd.init()
        self.font  = ImageFont.truetype(
             #'/usr/share/fonts/truetype/typewriter/MonospaceTypewriter.ttf', 10)
             '/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 10)

        #twitter      = Twython(KEYS['app_key'], KEYS['app_secret'], oauth_version=2)
        #self.twitter = Twython(KEYS['app_key'], access_token=twitter.obtain_access_token())
        self.twitter  = Twython(KEYS['app_key'], KEYS['app_secret'], 
                                KEYS['access_key'], KEYS['access_secret'])

        self.update()

        filterThread = Thread(target=self.filter)
        filterThread.start()

        self.run()


    def filter(self):

        while True:
            try:
                self.statuses.filter(follow=[self.TRUMP_ID])
            except:
                print('filter exception')


    def run(self):

        while True:
            # wait for an update from trump
            tweetId = self.queue.get()
            self.update(tweetId)


    def getTweet(self, tweetId):

        while True:
            try:
                timeline = self.twitter.get_user_timeline(
                    screen_name='realDonaldTrump', count=3, tweet_mode='extended')
            except:
                print('cannot get timeline')
                time.sleep(1)
                continue

            if tweetId is None:
                return timeline[0]

            for d in timeline:
                if d['id'] == tweetId:
                    return d
            
            time.sleep(1)


    def update(self, tweetId=None):

        retweet = False 
        reply   = False

        # get tweet json
        tweetdata = self.getTweet(tweetId)

        if 'retweeted_status' in tweetdata:
            retweet  = True
            tweet    = tweetdata['retweeted_status']['full_text']
            origUser = tweetdata['retweeted_status']['user']['screen_name']
        elif 'quoted_status' in tweetdata:
            reply    = True
            tweet    = tweetdata['full_text']
            origUser = tweetdata['quoted_status']['user']['screen_name']
        else:
            tweet    = tweetdata['full_text']

        print('')
        print(repr(tweet))
        print('')

        tweet = tweet.replace('&amp;', '&')
        tweet = tweet.replace('\n', ' ')
        tweet = tweet.replace('  ', ' ')

        tweetLines = self.splitTweet(tweet)

        if tweetLines == []:
            print('nothing left after formatting')
            return

        timestring   = tweetdata['created_at'] #.split('+')[0].strip()
        timestamp    = datetime.strptime(timestring, '%a %b %d %H:%M:%S %z %Y')
        timestamp    = timestamp.astimezone(timezone('Europe/Amsterdam'))
        timestring   = timestamp.strftime('%a %d %b %H:%M:%S')

        blackImage   = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        redImage     = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        blackDraw    = ImageDraw.Draw(blackImage)
        modulePath   = os.path.dirname(os.path.realpath(__file__))
        blackImgData = Image.open('{}/../images/baloon1.bmp'.format(modulePath))
        redImgData   = Image.open('{}/../images/baloon1_red.bmp'.format(modulePath))

        blackImage.paste(blackImgData, (0, 0))
        redImage.paste(redImgData, (0, 0))

        # draw tweet text
        for i, line in enumerate(tweetLines):
            blackDraw.text((10, 5 + 10 * i), line, font=self.font, fill=0)

        # draw some tweet metadata
        if retweet or reply:
            text = 'retweeted:' if retweet else 'replied to:'
            blackDraw.text((155, 80), text, font=self.font, fill=255)
            blackDraw.text((155, 92), '@' + origUser, font=self.font, fill=255)
            blackDraw.text((155, 104), '{}'.format(timestring), font=self.font, fill=255)
        else:
            blackDraw.text((155, 82), '{}'.format(timestring), font=self.font, fill=255)
        
        self.epd.display(self.epd.getbuffer(blackImage), self.epd.getbuffer(redImage))



    def on_success(self, data):

        if data['user']['id_str'] == self.TRUMP_ID:
            self.queue.put(data['id'])


    def on_error(self, status_code, data):
        print('Stream error: {}'.format(status_code))
        print(data)


    def on_exception(self, exception):
        print('exception')
        print(exception)


    def splitTweet(self, tweet):

        line = ''
        tweetLines = []

        for word in tweet.split(' '):

            if word[:8] == 'https://':
                continue

            if len(line) + len(word) + 1 <= 48:
                line += ' ' + word
            else:
                tweetLines.append(line)
                line = word

        if line != '':
            tweetLines.append(line)

        return tweetLines


def main():
    ticker = Ticker()


if __name__ == '__main__':
    main()
