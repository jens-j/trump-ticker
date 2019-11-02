#!/usr/bin/env python3

import epd2in7b                               # import the display drivers
from PIL import Image, ImageDraw, ImageFont   # import the image libraries

def getLine(s):
    line = ''


epd = epd2in7b.EPD()                          # get the display object and assing to epd
epd.init()                                    # initialize the display

font = ImageFont.truetype('/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 10)

blackImage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
redImage   = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)

tweet = ('I love New York, but New York can never be great again under the current leadership of '
       + 'Governor Andrew Cuomo (the brother of Fredo), or Mayor Bill DeBlasio. Cuomo has '
       + 'weaponized the prosecutors to do his dirty work (and to keep him out of jams), a reason '
       + 'some don’t want to be...')
tweetLines = []
line = ''
for word in tweet.split(' '):

    if len(line) + len(word) + 1 <= 48:
        line += ' ' + word
    else:
        tweetLines.append(line)
        line = word

if line != '':
    tweetLines.append(line)

image = Image.open('images/baloon1.bmp')
blackImage.paste(image, (0, 0))

blackDraw = ImageDraw.Draw(blackImage)
redDraw   = ImageDraw.Draw(redImage)
for i, line in enumerate(tweetLines):
    #blackDraw.text((5, 5 + 12 * i), line, font = font, fill = 0)
    redDraw.text(  (10, 3 + 10 * i), line, font = font, fill = 0)

print("Draw...")
epd.display(epd.getbuffer(blackImage), epd.getbuffer(redImage))
