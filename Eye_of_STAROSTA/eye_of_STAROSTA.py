import codecs
import configparser
import os
import random
import datetime
import sys
import json
from peewee import *
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Database.models import Day


# vk_session = VkApi(token='b427d2f68643c70505241dbcee1b2366e61eda1d9b6ad68f9bc2af2b31d7d0750775ac83c5a2070c811f1')

# session_api = vk_session.get_api()

# longpoll = VkLongPoll(vk_session)

config = configparser.RawConfigParser()
config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))

db_dir = config.get('database', 'dir')

db = SqliteDatabase(db_dir)


def create_keyboard(msg):
    keyboard = VkKeyboard(one_time=False)

    if msg == 'открыть меню' or msg == "вернутся в меню":

        keyboard.add_button('Расписание занятий',
                            color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Ближайшие задания',
                            color=VkKeyboardColor.PRIMARY)

        keyboard.add_line()
        keyboard.add_button('Вырубить бота нахуй',
                            color=VkKeyboardColor.PRIMARY)

    elif msg == 'привет' or msg == "начать":
        keyboard.add_button('Открыть меню', color=VkKeyboardColor.PRIMARY)

    else:
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send', {id_type: id, 'message': message, 'random_id': random.randint(
        -2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})


# def char():
#     for event in longpoll.listen():
#         if event.type == VkEventType.MESSAGE_NEW:
#             msg = event.text.lower()
#             keyboard = create_keyboard(msg)

#             if event.from_user and not event.from_me:
#                 print('Сообщение пришло в: ' +
#                     str(datetime.strftime(datetime.now(), "%H:%M:%S")))
#                 print('Текст сообщения: ' + str(event.text))
#                 print('ID пользователя: ' + str(event.user_id))
#                 print('-' * 30)

#                 if msg == "привет" or msg == "вернутся в меню" or msg == "начать":
#                     send_message(vk_session, 'user_id', event.user_id,
#                                 message='Вас приветствует учебный бот группы М3О-19Бк-19!', keyboard=keyboard)
#                 elif msg == "открыть меню":
#                     send_message(vk_session, 'user_id', event.user_id,
#                                 message='Учебное меню', keyboard=keyboard)
#                 elif msg == 'вырубить бота нахуй':
#                     send_message(vk_session, 'user_id', event.user_id,
#                                 message='ВЫРУБАЮСЬ НАХУЙ!')
#                     exit(-1)
#                 elif msg == 'закрыть':
#                     send_message(vk_session, 'user_id', event.user_id,
#                                 message='Закрыть', keyboard=keyboard)

#             elif event.from_chat:
#                 if msg == "привет":
#                     send_message(vk_session, 'chat_id',
#                                 event.chat_id, message='Привет!')
'''
req_dict = {
    'week': False or 'now' or 'next',
    'date': False or '25.09.21 etc.',
    'today': False or True
}
'''


def day_format(day):
    couples = []
    for couple in day:
        couples.append({
            'title': couple.subject_title,
            'type': couple.couple_type,
            'start_time': couple.couple_number.couple_start,
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
        req_data (str): Beautifulsoup
    """
    date = convert_date(date)
    day = Day.select().where(Day.date == date)
    return {str(date): day_format(day)}


def get_timetable_by_week():
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


def get_timetable_by_next_week():
    week_day = (datetime.datetime.now() + datetime.timedelta(days=1))
    while week_day.weekday() != 0:
        week_day += datetime.timedelta(days=1)
    return week_day

def get_timetable_by_day_of_week(day_of_week):
    pass


def get_timetable(req_data):
    timetable = {}
    if req_data.get('week'):
        if req_data.get('week') == 'next':
            week_day = get_timetable_by_next_week()
        else:
            week_day = get_timetable_by_week()
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
    else:
        print('SOME ERROR')  # TODO припилить логи


if __name__ == '__main__':
    req_dict = {
        'week': 0,
        'date': '12.10.2021',
        'today': 0,
        'day_of_week': 0
    }
    data = get_timetable(req_dict)
    with open('eye_of_STAROSTA/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
