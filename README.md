# Trump Ticker

## Hardware 

I use a raspberry 4B but I'm pretty sure that older pi's have the same pinout for the GPIO header so they should work too.
The display is a 2.7" three color e-paper display from waveshare. 

## Twitter Keys

The python script needs twitter API keys to get the twitter feed. If you dont have a twitter developer account you can apply for one [here](https://developer.twitter.com/en/apply-for-access.html). Afterwards you need to make an app which allows you to create API keys. 

These keys (2 pairs) need to be filled in `keys.sjon.template` after which you must rename the file to `keys.json`

## Run as Service
There are many ways on linux to run a program at startup. One of the proper ways is to run the program as a service. [Here is a nice explanation to do this.](https://tecadmin.net/setup-autorun-python-script-using-systemd/)

## Sources 
[Display documentation](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_(B))
[Display quick start guide](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)
[Twitter API documentation](https://developer.twitter.com/en/docs)
[Twitter API quick start guide](https://stackabuse.com/accessing-the-twitter-api-with-python/)
