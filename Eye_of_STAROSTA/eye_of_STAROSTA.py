import codecs
import configparser
import os
import random
import datetime
import sys
import json
import requests
from peewee import *
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiMethod

from parse_messages import parse_message

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Database.models import Day, File


config = configparser.RawConfigParser()
config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))

db_dir = config.get('database', 'dir')

db = SqliteDatabase(db_dir)


# def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
#     vk_session.method('messages.send', {id_type: id, 'message': message, 'random_id': random.randint(
#         -2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})


'''
req_dict = {
        'homework': False,
        'timetable': False,
        'actual': False,
        'week': False,
        'date': '25.09.2021',
        'tomorrow': False,
        'today': False,
        'day_of_week': False
    }
'''


def day_format(day):
    couples = []
    for couple in day:
        if couple.homework:
            homework = True
        else:
            homework = False
        couples.append({
            'title': couple.subject_title,
            'type': couple.couple_type,
            'start_time': couple.couple_number.couple_start,
            'homework': homework,
        })
    return couples


def homework_format(homework):
    couples = []
    for couple in homework:
        files = File.select().where(
            File.homework_date == couple.date,
            File.subject_title == couple.subject_title,
            File.couple_type == couple.couple_type
        )
        files_list = []
        for file in files:
            data = {
                'verbose_name': file.verbose_name,
                'file_name': file.file_name,
                'link': file.link,
            }
            files_list.append(data)
        couples.append({
            'title': couple.subject_title,
            'type': couple.couple_type,
            'homework': couple.homework,
            'files': files_list,
        })
    return couples


def convert_date(date):
    if type(date) is str:
        try:
            date = datetime.datetime.strptime(
                date, '%d.%m.%Y').date()
            return date
        except:
            date = datetime.datetime.strptime(
                date, '%Y-%m-%d').date()
            return date
    if type(date) == datetime.datetime:
        return date.date()
    print('SOME ERROR')  # TODO припилить логи


def get_timetable_by_date(date):
    """Get timetable by date from html req_data

    Args:
        date (str)
    """
    date = convert_date(date)
    day = Day.select().where(Day.date == date)
    return {str(date): day_format(day)}


def get_homework_by_date(date):
    """Get homework by date from html req_data

    Args:
        date (str) 
    """
    date = convert_date(date)
    homework = Day.select().where(Day.date == date, Day.homework != None)
    return {str(date): homework_format(homework)}


def get_week():
    """
    Get timetable by week from html req_data
    """
    week_day = (datetime.datetime.now())
    while week_day.weekday() != 0:
        week_day += datetime.timedelta(days=-1)
    return week_day


def get_timetable_today():
    """
        function return timetalble for today
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    return get_timetable_by_date(today)


def get_homework_today():
    """
        function return homework for today
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    return get_homework_by_date(today)


def get_timetable_tomorrow():
    """
        function return timetable for tomorrow
    """
    tomorrow = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    return get_timetable_by_date(tomorrow)


def get_homework_tomorrow():
    """
        function return homework for tomorrow
    """
    tomorrow = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    return get_homework_by_date(tomorrow)


def get_next_week():
    week_day = (datetime.datetime.now() + datetime.timedelta(days=1))
    while week_day.weekday() != 0:
        week_day += datetime.timedelta(days=1)
    return week_day


def get_timetable_by_day_of_week(day_of_week):
    day = (datetime.datetime.now())
    while day.weekday() != day_of_week:
        day += datetime.timedelta(days=1)
    return get_timetable_by_date(day)


def get_homework_by_day_of_week(day_of_week):
    day = (datetime.datetime.now())
    while day.weekday() != day_of_week:
        day += datetime.timedelta(days=1)
    return get_homework_by_date(day)


def get_homework(req_data):
    homework = {}
    if req_data.get('week'):
        if req_data.get('week') == 'next':
            week_day = get_next_week()
        else:
            week_day = get_week()
        for _ in range(6):
            homework.update(get_homework_by_date(week_day))
            week_day += datetime.timedelta(days=1)
        return homework
    elif req_data.get('date'):
        return get_homework_by_date(req_data.get('date'))
    elif req_data.get('today'):
        return get_homework_today()
    elif req_data.get('day_of_week'):
        return get_homework_by_day_of_week(req_data.get('day_of_week'))
    elif req_data.get('tommorow'):
        return get_homework_tomorrow()
    elif req_data.get('actual'):
        day = datetime.datetime.now()
        for _ in range(4):
            item = get_homework_by_date(day)
            while item[str(day.date())] == []:
                day += datetime.timedelta(days=1)
                item = get_homework_by_date(day)
            homework.update(item)
            day += datetime.timedelta(days=1)
        return homework
    else:
        print('SOME ERROR')  # TODO припилить логи


def get_timetable(req_data):
    timetable = {}
    if req_data.get('week'):
        if req_data.get('week') == 'next':
            week_day = get_next_week()
        else:
            week_day = get_week()
        for _ in range(6):
            timetable.update(get_timetable_by_date(week_day))
            week_day += datetime.timedelta(days=1)
        return timetable
    elif req_data.get('date'):
        return get_timetable_by_date(req_data.get('date'))
    elif req_data.get('today'):
        return get_timetable_today()
    elif req_data.get('day_of_week'):
        return get_timetable_by_day_of_week(req_data.get('day_of_week'))
    elif req_data.get('tommorow'):
        return get_timetable_tomorrow()
    elif req_data.get('actual'):
        day = datetime.datetime.now()
        for _ in range(4):
            item = get_timetable_by_date(day)
            while item[str(day.date())] == []:
                day += datetime.timedelta(days=1)
                item = get_timetable_by_date(day)
            timetable.update(item)
            day += datetime.timedelta(days=1)
        return timetable
    else:
        print('SOME ERROR')  # TODO припилить логи

def get_db_response(req_dict):
    if req_dict.get('timetable'):
        get_timetable(req_dict)
    elif req_dict.get('homework'):
        get_homework(req_dict)
    else:
        pass  # TODO добавить обработку ошибки


def group_msg():
    while True:
        vk = VkApi(
            token='b427d2f68643c70505241dbcee1b2366e61eda1d9b6ad68f9bc2af2b31d7d0750775ac83c5a2070c811f1')
        long_poll = VkBotLongPoll(vk, 186214698)
        vk_api = vk.get_api()
        try:
            for event in long_poll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    try:
                        msg = event.object['message']['text']
                        req_data = parse_message(msg)
                        values = {
                        'message': str(get_db_response(req_data)),
                        'peer_id': event.object['message']['peer_id'],
                        'random_id': random.randint(0, 1024)}
                        vk.method('messages.send', values=values)
                    except Exception as e:
                        print(e)
        except requests.exceptions.ReadTimeout as timeout:
            continue


if __name__ == '__main__':
    # req_dict = {
    #     'homework': False,
    #     'timetable': False,
    #     'actual': False,
    #     'week': False,
    #     'date': '25.09.2021',
    #     'tomorrow': False,
    #     'today': False,
    #     'day_of_week': False
    # }
    # data = get_homework(req_dict)
    # with open('eye_of_STAROSTA/data.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4, ensure_ascii=False)
    group_msg()
