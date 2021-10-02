import urllib.request
import json
import requests
import time
import os
from datetime import datetime
import logging
from telegram.ext import Updater

api_key = os.environ['NOMICS_API_KEY']

urlgas = "https://api.nomics.com/v1/currencies/ticker?key=" + api_key + "&ids=ETH&interval=1m&convert=USD&per-page=100&page=1"

def getgas():
    # get USD-ETH price conversion:
    weitoeth = 1e13
    pricedata = json.load(urllib.request.urlopen(urlgas))
    ethusd = float(pricedata[0]['price'])
    # get current GAS fees (in wei)
    data = json.load(urllib.request.urlopen('https://www.gasnow.org/api/v3/gas/price?utm_source=:WHACKD'))
    if data['code'] != 200:
        Exception("failed")
    else:
        rapid     = "{:.2f}".format((data['data']['rapid'] / weitoeth) * ethusd)
        fast      = str( (int(data['data']['fast'])     / weitoeth ) * ethusd )
        standard  = str( (int(data['data']['standard']) / weitoeth ) * ethusd )
        slow      = str( (int(data['data']['slow'])     / weitoeth ) * ethusd )
        timestamp = str(datetime.fromtimestamp(data['data']['timestamp'] / 1000))
        
    return "Current ETH price and gas fees:" + "\nETH price: $" + str(ethusd) + "\nrapid: $" + str(rapid) + "\nfast: $" + fast + "\nstandard: $" + standard + "\nslow: $" + slow + "\ntimestamp: " + timestamp

print(getgas())