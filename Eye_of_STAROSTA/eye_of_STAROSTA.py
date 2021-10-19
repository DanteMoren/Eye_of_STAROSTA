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

sys.path.insert(0, "./database")

from models import Day, File


config = configparser.RawConfigParser()
config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))

db_dir = config.get('database', 'dir')

db = SqliteDatabase(db_dir)


emojies = {
    'Физическая культура (спортивные секции)': '💪Физическая культура (спортивные секции)',
    'Иностранный язык': '🏳️‍🌈Иностранный язык',
    'Архитектуры вычислительных систем': '🛌Архитектуры вычислительных систем',
    'Основы психологии': '🧐Основы психологии',
    'Конструирование программного обеспечения': '👴Конструирование программного обеспечения',
    'Экономика': '📈Экономика',
    'Математическое программирование': '😴Математическое программирование',
    'Теория игр и методы принятия решений': '👾Теория игр и методы принятия решений',
    'Аналитическое моделирование': '⚽Аналитическое моделирование',
    'Физическая культура': '💪Физическая культура',
    'Военная подготовка': '🌈Военная подготовка',
    'Основы психологии': '🧐Основы психологии',
    'Вычислительная математика': '💻Вычислительная математика',
    'Социология': '🤡Социология',
    'Обработка экспериментальных данных на ЭВМ или Математическое программирование':'👨‍🔧Обработка экспериментальных данных на ЭВМ или 😴Математическое программирование',
    'Конструирование программного обеспечения': '👴Конструирование программного обеспечения',
    'Обработка экспериментальных данных на ЭВМ': '👨‍🔧Обработка экспериментальных данных на ЭВМ',
}



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
            'weekday': couple.day_of_week,
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
    print('SOME ERROR CONVERWT')  # TODO припилить логи


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
    elif req_data.get('tomorrow'):
        return get_homework_tomorrow()
    elif req_data.get('actual'):
        day = datetime.datetime.now()
        for _ in range(8):
            item = get_homework_by_date(day)
            iterations = 0
            while item[str(day.date())] == [] and iterations != 5:
                day += datetime.timedelta(days=1)
                item = get_homework_by_date(day)
                iterations +=1
            homework.update(item)
            day += datetime.timedelta(days=1)
        return homework
    else:
        print('SOME ERROR GET HOMEWORK')  # TODO припилить логи


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
    elif req_data.get('tomorrow'):
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
        print('SOME ERROR GET TIMETABLE')  # TODO припилить логи

def get_db_response(req_dict):
    if req_dict is not None:
        if req_dict.get('timetable'):
            return get_timetable(req_dict)
        elif req_dict.get('homework'):
            return get_homework(req_dict)


def compare_answer(answer, req_dict):
    compared_answer = ''
    if req_dict['timetable']:
        for date in answer:
            if answer[date] == []:
                continue
            data = answer[date]
            compared_answer += (f'\n\t📅{date}, {answer[date][0]["weekday"]}\n\n')
            for couple in data:
                if couple["type"] == 'ЛР':
                    compared_answer += (
                        f'\t{emojies[couple["title"]]}, ❗ЛР❗ - начинается в '
                        f'{couple["start_time"]}')
                else:
                    compared_answer += (
                        f'\t{emojies[couple["title"]]}, {couple["type"]} - начинается в ' 
                        f'{couple["start_time"]}')
                if couple["homework"]:
                    compared_answer += ' есть домашнее задание❗'
                compared_answer += '\n'
    elif req_dict['homework']:
        for date in answer:
            if answer[date] == []:
                continue
            data = answer[date]
            compared_answer += (f'\n\t📅{date} \n\n')
            for couple in data:
                files = [file['link'] for file in couple['files']]
                compared_answer += (
                    f'\t{emojies[couple["title"]]}, {couple["type"]}:\n' 
                    f'{couple["homework"]}\n\n')
                if files != []:
                    compared_answer += (f'Прикрепленные файлы: {files}')
        if compared_answer == '':
            return 'Ну, лично я вообще понятия не имею что там задали. По такому-то запросу🙄'
        
    
    else:
        pass # TODO написать ошибку
    if compared_answer == '':
        return 'Слушай, чет пошло не по плану. Наташа! Мы все уронили!'
    return compared_answer

"""
def attachment_init(attach):
    pass
    return 
    
"""
def group_msg():
    while True:
        vk = VkApi(token='b427d2f68643c70505241dbcee1b2366e61eda1d9b6ad68f9bc2af2b31d7d0750775ac83c5a2070c811f1')
        long_poll = VkBotLongPoll(vk, 186214698)
        vk_api = vk.get_api()
        try:
            for event in long_poll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    try:
                        msg = event.object['message']['text']
                        req_dict = parse_message(msg)
                        if req_dict is not None:
                            answer = (get_db_response(req_dict))
                            message = str(compare_answer(answer, req_dict))
                            values = {
                            'message': message,
                            'peer_id': event.object['message']['peer_id'],
                            'random_id': random.randint(0, 1024)}
                            # 'attachment': f'photo{owner_id}_{photo_id}_{access_key}'
                            vk.method('messages.send', values=values)
                    except Exception as e:
                        print(e)
        except requests.exceptions.ReadTimeout as timeout:
            continue


if __name__ == '__main__':
    # req_dict = {
    #     'homework': False,
    #     'timetable': True,
    #     'actual': False,
    #     'week': False,
    #     'date': '10.02.2021',
    #     'tomorrow': False,
    #     'today': False,
    #     'day_of_week': False
    # } 
    # data = get_db_response(req_dict)
    # print(compare_answer(data, req_dict))
    # with open('eye_of_STAROSTA/data.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4, ensure_ascii=False)
    group_msg()
