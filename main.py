import os
from telebot import TeleBot
import json
from datetime import date, datetime, time, timedelta
import plotly.express as px
from platform import system
from rich import print
from collections import defaultdict

API_KEY = "2095864231:AAGOdA4LGq9w3CajxhWJvuPpaWUUocvfJHg"
MY_ID = 28076818

bot = TeleBot(API_KEY)

last_info_id = 0

STANDARD_OPTIONS= ''' Usual activities:

/yesterday
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
/gaming

/eating
/snacking
/sleep
/nap

/dubious
'''

INFO_COMMANDS = ["/info", "/info_week", "/yesterday"]
time_diff = timedelta(hours=1) if system() == "Linux" else timedelta(0)

@bot.message_handler(func=lambda message: message.text[0] != "/")
def arb_entry(message): # for arbitrary entries without "/"
    global last_info_id
    if message.from_user.id == MY_ID:
        chat_id = message.chat.id
        if "info" not in message.text.lower(): 
            enter_activity(message.text.lower(), datetime.now()+time_diff)
        send_info(chat_id)


@bot.message_handler(func=lambda message: message.text[0] == "/")
def command_handler(message):
    chat_id = message.chat.id
    if message.from_user.id == MY_ID:
        if "info" in message.text.lower():
            if "week" in message.text.lower():
                send_week_chart(chat_id)
            else:
                send_day_chart(chat_id, "image.png", datetime.now())
        if "/yesterday" in message.text.lower():
            send_day_chart(chat_id, "image.png", datetime.now()-timedelta(days=1))
        elif not any(x in message.text.lower() for x in INFO_COMMANDS) in message.text.lower():
            enter_activity(message.text[1:], datetime.now()+time_diff)
        send_info(chat_id)

        

def send_info(chat_id):
    global last_info_id
    try:
        bot.delete_message(chat_id, last_info_id)
    except:
        pass
    last_info_id = bot.send_message(chat_id, STANDARD_OPTIONS).id

def send_day_chart(chat_id, filename, date):
    str_date = str(date)[:10]
    day_chart(str_date, "image.png")
    img = open(filename, "rb")
    bot.send_photo(chat_id, img)
    img.close()


def send_week_chart(chat_id):
    num_images = week_chart()
    for i in range(num_images):
        send_day_chart(chat_id, f"image{i}.png")
        os.remove(f"image{i}.png")



def enter_activity(status, in_time):
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

    
# #7D99D9
def day_chart(date, image_filename):
    all_data = json.load(open("log.json", "r"))
    data = all_data[date]

    activity_dict = defaultdict(timedelta)
    last_key = "00:00"
    for key in data:
        last_time = timedelta(hours= int(last_key[0:2]), minutes= int(last_key[3:5]))
        now_time = timedelta(hours= int(key[0:2]), minutes= int(key[3:5]))

        delta = now_time - last_time

        activity_dict[data[key]] += delta
        last_key = key
    next_day, _ = next_date(date)
    if next_day in all_data:
        time1 = list(data.keys())[-1]
        time_2nd_day = list(all_data[next_day].keys())[0]
        time2 = time_2nd_day
        delta = two_day_time_diff(time1, time2)

        activity_dict[all_data[next_day][time_2nd_day]] += delta


    labels = [t for t in activity_dict.keys()]
    times = [activity_dict[key].total_seconds() for key in activity_dict.keys()]

    fig = px.pie(values=times, names=labels, title=date)
    fig.write_image(image_filename)
    return times, labels


def next_date(date):
    datetime_date = datetime(year= int(date[:4]), month=int(date[5:7]), day=int(date[-2:])) + timedelta(days=1)
    next_day = str(datetime_date)[:10]
    return next_day, datetime_date


def two_day_time_diff(time1, time2):
    # parameters as strings like "21:00"
    h1, m1, h2, m2 = int(time1[:2]), int(time1[-2:]), int(time2[:2]), int(time2[-2:])
    delta1 = timedelta(days=0, hours= h1, minutes=m1)
    delta2 = timedelta(days=1, hours= 0, minutes=0)

    return delta2-delta1


def week_chart():
    today_date = str(datetime.now())[:10]
    data = json.load(open("log.json", "r"))
    keys = list(data.keys())
    date_index = keys.index(today_date)
    total_times = []
    total_labels = []
    if date_index < 6:
        dates = keys[:date_index+1]
    else:
        dates = keys[date_index-6:date_index+1]
    for i, date in enumerate(dates):
        times, labels = day_chart(date, f"image{i}.png")
        total_times += times
        total_labels += labels
    fig = px.pie(values=total_times, names=total_labels, title="WEEK "+dates[0]+" <-> "+today_date)
    fig.write_image(f"image{i+1}.png")
    return len(dates)+1


bot.infinity_polling()
# day_chart("2021-11-23", "test_image.png")