#!/usr/bin/env python3
#
# from collection import deque
import os
import time
import pprint
from queue import Queue
from threading import Thread
from datetime import datetime, tzinfo
from pytz import timezone
import epd2in7b
from PIL import Image, ImageDraw, ImageFont
from twython import Twython, TwythonStreamer
import http.client


class Ticker(TwythonStreamer):

    APP_KEY       = '3YkdRq6EcjZZP52H2G1Xr7USq'
    APP_SECRET    = 'nubk75G1LBwg2uZI5CUK2fVrnG91BF94rcCAFgL0Rj7DKBufzO'
    ACCESS_KEY    = '1190403948156477440-QW3dvfPd2722VdEd3cA683DewpZEB1'
    ACCESS_SECRET = 'O11jWcr8Zb7ATgAtbi8PIGkF24CwmNsyCClMKI1LAMfnR'
    TRUMP_ID      = '25073877'

    def __init__(self):

        super(Ticker, self).__init__(
            self.APP_KEY, self.APP_SECRET, self.ACCESS_KEY, self.ACCESS_SECRET)

        #http.client.HTTPConnection._http_vsn = 10
        #http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        self.pp    = pprint.PrettyPrinter()
        self.queue = Queue()
        self.epd   = epd2in7b.EPD()
        self.epd.init()
        self.font  = ImageFont.truetype(
             #'/usr/share/fonts/truetype/typewriter/MonospaceTypewriter.ttf', 10)
             '/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 10)

        #twitter      = Twython(self.APP_KEY, self.APP_SECRET, oauth_version=2)
        #self.twitter = Twython(self.APP_KEY, access_token=twitter.obtain_access_token())
        self.twitter  = Twython(self.APP_KEY, self.APP_SECRET, self.ACCESS_KEY, self.ACCESS_SECRET)

        self.update()

        filterThread = Thread(target=self.filter)
        # filterThread = Thread(target=self.statuses.filter,
        #                       kwargs={'track': ['from:{:s}'.format(self.TRUMP_ID)]}) # -filter:media -filter:links
        filterThread.start()

        # mainThread = Thread(target=self.run)
        # mainThread.start()
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
            
            # self.pp.pprint(timeline)
            # print('tweet not in timeline')
            # print([x['id'] for x in timeline])
            time.sleep(1)


    def update(self, tweetId=None):

        # print("update {}".format(tweetId))
        # print(type(tweetId))

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

        # print(len(tweetdata))
        # print(len(timeline))
        # self.pp.pprint(timeline[0])

        #tweet = 'The Amazon Washington Post and three lowlife reporters, Matt Zapotosky, Josh Dawsey, and Carol Leonnig, wrote another Fake News story, without any sources (pure fiction), about Bill Barr & myself. We both deny this story, which they knew before they wrote it. A garbage newspaper!'

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
        blackImgData = Image.open('{}/../images/baloon2.bmp'.format(modulePath))
        #redImgData   = Image.open('{}/../images/baloon1_red.bmp'.format(modulePath))

        blackImage.paste(blackImgData, (0, 0))
        #redImage.paste(redImgData, (0, 0))

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

        # print(data['created_at'])
        # print(data['text'])

        if data['user']['id_str'] == self.TRUMP_ID:

            #print('')
            #self.pp.pprint(data)
            # print('on_success')
            # print(data['id'])
            self.queue.put(data['id'])


    def on_error(self, status_code, data):
        print('Stream error: {}'.format(status_code))
        print(data)


    def on_exception(self, exception):
        print('exception')
        print(exception)
        return


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
