import os
from telebot import TeleBot
import json
from datetime import date, datetime, time, timedelta
from matplotlib import pyplot as plt
import plotly.express as px

API_KEY = "2095864231:AAGOdA4LGq9w3CajxhWJvuPpaWUUocvfJHg"
MY_ID = 28076818

bot = TeleBot(API_KEY)

last_info_id = 0

STANDARD_OPTIONS= ''' Usual activities:

/info
/info_week

/programming
/youtube
/cinema
/math
/school
/homework
/school_study

/friends
/party
/reading

/eating
/snacking
/sleep
/nap
'''


@bot.message_handler(func=lambda message: message.text[0] != "/")
def arb_entry(message): # for arbitrary entries without "/"
    global last_info_id
    if message.from_user.id == MY_ID:
        chat_id = message.chat.id
        if "info" not in message.text.lower(): 
            enter_activity(message.text.lower(), datetime.now())
        send_info(chat_id)


@bot.message_handler(func=lambda message: message.text[0] == "/")
def command_handler(message):
    chat_id = message.chat.id
    if message.from_user.id == MY_ID:
        if "info" in message.text.lower():
            if "week" in message.text.lower():
                print("weeking")
                send_week_chart(chat_id)
            else:
                send_day_chart(chat_id, "image.png")
        else:
            enter_activity(message.text[1:], datetime.now())
        send_info(chat_id)

        

def send_info(chat_id):
    global last_info_id
    try:
        bot.delete_message(chat_id, last_info_id)
    except:
        pass
    last_info_id = bot.send_message(chat_id, STANDARD_OPTIONS).id

def send_day_chart(chat_id, filename):
    today_chart()
    img = open(filename, "rb")
    bot.send_photo(chat_id, img)
    img.close()


def send_week_chart(chat_id):
    num_images = week_chart()
    for i in range(num_images):
        send_day_chart(chat_id, f"image{i}.png")
        os.remove(f"image{i}.png")



def enter_activity(status, in_time):
    in_time: datetime
    log = {}
    with open("log.json", "r") as log:
        log = json.load(log)
    date = str(in_time)[:10]
    in_time = str(in_time)[11:16]
    if date not in log:
        log[date] = dict()
    log[date][in_time] = str(status)
    
    with open("log.json", "w") as log_file:
        json.dump(log, log_file)


def today_chart():
    date = str(datetime.now())[:10]
    day_chart(date, "image.png")
    
# #7D99D9
def day_chart(date, filename):
    data = json.load(open("log.json", "r"))[date]

    activity_dict = {}
    last_key = "00:00"
    for key in data:
        last_time = timedelta(hours= int(last_key[0:2]), minutes= int(last_key[3:5]))
        now_time = timedelta(hours= int(key[0:2]), minutes= int(key[3:5]))

        delta = now_time - last_time

        activity_dict[delta] = data[key]
        last_key = key
    times = [t.total_seconds() for t in activity_dict.keys()]
    labels = [activity_dict[key] for key in activity_dict.keys()]

    print(activity_dict)
    fig = px.pie(values=times, names=labels, title=date)
    fig.write_image(filename)


def week_chart():
    today_date = str(datetime.now())[:10]
    data = json.load(open("log.json", "r"))
    keys = list(data.keys())
    date_index = keys.index(today_date)
    if date_index < 6:
        dates = keys[:date_index+1]
    else:
        dates = keys[date_index-6:date_index+1]
    for i, date in enumerate(dates):
        day_chart(date, f"image{i}.png")
    return len(dates)


bot.infinity_polling()