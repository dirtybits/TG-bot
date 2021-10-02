# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

import urllib.request
import os
import json
import requests
import time
from datetime import datetime
import logging
import telegram.ext
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

api_key = os.environ['NOMICS_API_KEY']
bot_api_key = os.environ['TG_API_KEY']

# For update timers in seconds
hour = 3600 
day = hour * 24
# API for prices
url = "https://api.nomics.com/v1/currencies/ticker?key=" + api_key + "&ids=WHACKD&interval=1m&convert=USD&per-page=100&page=1"

urlgas = "https://api.nomics.com/v1/currencies/ticker?key=" + api_key + "&ids=ETH&interval=1m&convert=USD&per-page=100&page=1"

wgwurl = "https://whosgettingwhackd.com/"

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')
    
def pricehelp(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I am a price bot, I was built specifically for $WHACKD! Here are my commands:\n -/start \n -/pricehelp \n -/settings \n -/price \n -/counter \n -/gas \n If you have any feedback, please let the bot developer @dirtybits know!  Thanks!")

def settings(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="currently I only handle ETH gas and $WHACKD prices")
    
def getprice():
    data = json.load(urllib.request.urlopen(url))
    symbol = data[0]['symbol']
    price = data[0]['price']
    timestamp = data[0]['price_timestamp']
    supply = "{:,}".format(int(data[0]['max_supply']))
    burn = "{:,.4f}".format((1e9 - int(int(data[0]['max_supply'])))/(1e9) * 100)
    
    return '$' + symbol + ' (provided by nomics.com)\n[PRICE]: $' + price + '\n[SUPPLY]: ' + supply + ' $' + symbol + '\n[BURNT]: ' + burn + '%' + '\n[TIME]: ' + timestamp
    
def price(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=getprice())
    
# def counter(update, context):
    # Transactions until next WHACK: 500
    # url = wgwurl
    # html_doc = requests.get(url).content
    # soup = BeautifulSoup(html_doc, 'html.parser')
    # # counter_container = soup.find("div", {"class": "text-lg font-semibold text-gray-100"}).get_text().strip()
    # print(counter_container)
    
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
        rapid     = "{:.2f}".format((int(data['data']['rapid'])    / weitoeth ) * ethusd )
        fast      = "{:.2f}".format((int(data['data']['fast'])     / weitoeth ) * ethusd )
        standard  = "{:.2f}".format((int(data['data']['standard']) / weitoeth ) * ethusd )
        slow      = "{:.2f}".format((int(data['data']['slow'])     / weitoeth ) * ethusd )
        timestamp = str(datetime.fromtimestamp(data['data']['timestamp'] / 1000))

    return "\nCurrent ETH Gas Prices (provided by gasnow.org):" + "\n[ETH Price]: $" + "{:.2f}".format(ethusd) + "\n[Rapid]: $" + rapid + "\n[Fast]: $" + fast + "\n[Standard]: $" + standard + "\n[Slow]: $" + slow + "\n[Timestamp]: " + timestamp
    
def gas(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=getgas())
    
def callback_minute(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id='@WHACKDByMcAfeeBasedChat', text=getprice() + getgas() + "\nPlease contact the bot developer @dirtybits for feedback or feature requests.")
    
def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


# def reminder(conte)

#  @TO-DO 
# Joshua Bimbane, [19.08.21 00:48]
# Can we get the pricebot to show 1HR, 12HR, 1Day, 1 week change and volume and liquidity?
# def burn counter()
# def get last WHACKD TX
# * hourly updates (including price change in %)
# * automatically inform the channel when a price-change was more than 10% in a certain time
# * alert when gas fees are high
# marketcap of WHACKD
# WHACKD/ETH or WHACKD/WETH rates
# /price@combot
# is it possible to make a bot that automatically warns us when only 10 transactions remain before the big whack?

def main() -> None:
    
    updater = Updater(token=bot_api_key, use_context=True)
    
    jobq = updater.job_queue

    dispatcher = updater.dispatcher
    
    start_handler = CommandHandler('start', start)
    pricehelp_handler = CommandHandler('pricehelp', pricehelp)
    settings_handler = CommandHandler('settings', settings)
    price_handler = CommandHandler('price', price)
    # counter_handler = CommandHandler('counter', counter)
    gas_handler = CommandHandler('gas', gas)
    

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(pricehelp_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(price_handler)
    dispatcher.add_handler(gas_handler)
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    
    
    updater.start_polling()
    
    jobq.run_repeating(callback_minute, interval=hour*2, first=10)

    updater.idle()
    
if __name__ == "__main__":
    main()