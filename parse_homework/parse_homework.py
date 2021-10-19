# -*- coding: utf-8 -*-
import configparser
import os
import requests
import codecs
import re
import sys
from fake_useragent import UserAgent
from dotenv import load_dotenv

sys.path.insert(0, "/opt/database")

from models import add_homework

subject_title_list = [
    'Иностранный_язык', 'Архитектуры_вычислительных_систем',
    'Основы_психологии', 'Конструирование_программного_обеспечения',
    'Вычислительная_математика', 'Экономика',
    'Математическое_программирование', 'Теория_игр_и_методы_принятия_решений',
    'Аналитическое_моделирование', 'Социология',
    'Обработка_экспериментальных_данных_на_ЭВМ'
]


def get_homework_data(text):
    homework = re.search(r'\n[^#]+', text)[0]
    homework = re.sub(
        r'(\d{2}\.\d{2}\.\d{4})|(\d{2}\.\d{2}\.\d{2})', '', homework
    ).strip()
    date = re.search(r'(\d{2}\.\d{2}\.\d{4})|(\d{2}\.\d{2}\.\d{2})', text)
    for title in subject_title_list:
        subject_title = re.search(title, text)
        if subject_title:
            couple_type = text[subject_title.end()+1:subject_title.end()+3]
            subject_title = re.sub('_', ' ', subject_title[0])
            break

    if date and subject_title:
        if re.search(r'^\d{2}\.\d{2}\.\d{2}$', date[0]):
            date = date[0][:6] + '20' + date[0][6:]
        else:
            date = date[0]
        return {
            'title': subject_title,
            'type': couple_type,
            'homework': homework,
            'date': date
        }
    #  TODO накинуть логи
    return {}


def parse_homework():

    load_dotenv()
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')

    config = configparser.RawConfigParser()
    config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))
    DOMAIN = config.get('homework', 'domain')
    VK_API_VERSION = config.get('homework', 'vk_api_version')

    useragent = UserAgent()
    headers = {
        'Accept': '*/*',
        'User-Agent': f'{useragent.random}'
    }

    url = 'https://api.vk.com/method/wall.get'
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_API_VERSION,
        'domain': DOMAIN
    }

    req = requests.get(url, headers=headers, params=params)
    if req.status_code != 200:
        print('ОНО НАЕБНУЛОСЬ')  # TODO сделать ошибку
        return
    # TODO сделать ошибку, req.json()['error'] или что-то такое, когда сломан токен
    posts = req.json()['response']['items'][1:10]

    homework = []
    for post in posts:
        if '#ДЗ@m3o_19bk_19' in post.get('text'):
            files = []
            attachments = post.get('attachments')
            if attachments:
                for attach in post.get('attachments'):
                    if attach['type'] == 'photo':
                        link = attach['photo']['sizes'][-1]['url']
                        name = str(attach['photo']['id'])
                        files.append({'name': name, 'link': link})
                    elif attach['type'] == 'doc':
                        link = attach['doc']['url']
                        name = attach['doc']['title']
                        files.append({'name': name, 'link': link})

            data = {
                'files': files
            }
            data.update(get_homework_data(post.get('text')))
            # проверка на наличие правильного заголовка и даты
            try:
                if data.get('title') and data.get('date'):
                    homework.append(data)
            except KeyError:
                continue
    return homework


if __name__ == '__main__':
    data = parse_homework()
    for homework in data:
        add_homework(homework)
