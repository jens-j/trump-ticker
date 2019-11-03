#!/usr/bin/env python3
#
# from collection import deque
import os
from queue import Queue
from threading import Thread
import epd2in7b
from PIL import Image, ImageDraw, ImageFont
from twython import Twython, TwythonStreamer
#import daemon

class Ticker(TwythonStreamer):

    APP_KEY       = '3YkdRq6EcjZZP52H2G1Xr7USq'
    APP_SECRET    = 'nubk75G1LBwg2uZI5CUK2fVrnG91BF94rcCAFgL0Rj7DKBufzO'
    ACCESS_KEY    = '1190403948156477440-QW3dvfPd2722VdEd3cA683DewpZEB1'
    ACCESS_SECRET = 'O11jWcr8Zb7ATgAtbi8PIGkF24CwmNsyCClMKI1LAMfnR'
    TRUMP_ID      = '25073877'

    def __init__(self):

        super(Ticker, self).__init__(self.APP_KEY, self.APP_SECRET, self.ACCESS_KEY, self.ACCESS_SECRET)

        self.queue = Queue()
        self.epd = epd2in7b.EPD()
        self.epd.init()
        self.font = ImageFont.truetype(
            '/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 10)

        twitter      = Twython(self.APP_KEY, self.APP_SECRET, oauth_version=2)
        self.twitter = Twython(self.APP_KEY, access_token=twitter.obtain_access_token())

        self.update()

        filterThread = Thread(target=self.statuses.filter, kwargs={'follow': [self.TRUMP_ID]})
        filterThread.start()

        mainThread = Thread(target=self.run)
        selmainThreadf.start()


    def run(self):

        while True:
            # wait for an update from trump
            self.queue.get()
            print("update")
            self.update()


    def update(self):

        # get full tweet text
        timeline = self.twitter.get_user_timeline(
            screen_name='realDonaldTrump', count=1, tweet_mode='extended')

        tweetLines = self.splitTweet(timeline[0]['full_text'])

        blackImage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        redImage   = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
        blackDraw  = ImageDraw.Draw(blackImage)
        modulePath = os.path.dirname(os.path.realpath(__file__))
        image      = Image.open('{}/../images/baloon1.bmp'.format(modulePath))

        blackImage.paste(image, (0, 0))
        for i, line in enumerate(tweetLines):
            blackDraw.text((10, 3 + 10 * i), line, font=self.font, fill=0)

        self.epd.display(self.epd.getbuffer(blackImage), self.epd.getbuffer(redImage))


    def on_success(self, data):

        if data['user']['id_str'] == self.TRUMP_ID:
            self.queue.put(1)


    def on_error(self, status_code, data):
        print('Stream error: {}'.format(status_code))


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
