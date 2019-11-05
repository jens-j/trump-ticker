#!/usr/bin/env python3
#
# from collection import deque
import os
import time
import pprint
from queue import Queue
from threading import Thread
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
            self.queue.get()
            print("update")
            self.update()


    def update(self):

        # get full tweet text
        while True:
            try:
                timeline = self.twitter.get_user_timeline(
                    screen_name='realDonaldTrump', count=5, tweet_mode='extended')
                tweetdata = timeline[0]
                break
            except:
                print('cannot get timeline')
                time.sleep(1)

        if 'retweeted_status' in tweetdata:
            tweet = tweetdata['retweeted_status']['full_text']
        else:
            tweetdata['full_text']

        # print(len(tweetdata))

        # self.pp.pprint(tweetdata)
        print(tweet)

        tweetLines   = self.splitTweet(tweet)
        blackImage   = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        redImage     = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        blackDraw    = ImageDraw.Draw(blackImage)
        modulePath   = os.path.dirname(os.path.realpath(__file__))
        blackImgData = Image.open('{}/../images/baloon1.bmp'.format(modulePath))
        redImgData   = Image.open('{}/../images/baloon1_red.bmp'.format(modulePath))

        blackImage.paste(blackImgData, (0, 0))
        redImage.paste(redImgData, (0, 0))

        for i, line in enumerate(tweetLines):
            blackDraw.text((10, 5 + 10 * i), line, font=self.font, fill=0)

        self.epd.display(self.epd.getbuffer(blackImage), self.epd.getbuffer(redImage))


    def on_success(self, data):

        # print('')
        # print(data['created_at'])
        # print(data['text'])

        if data['user']['id_str'] == self.TRUMP_ID:
            self.queue.put(1)


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
