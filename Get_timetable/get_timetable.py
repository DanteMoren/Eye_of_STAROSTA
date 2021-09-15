import configparser
import os
import codecs
import requests
import datetime
import sys
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Database.models import *

def parse_timetable():
    """Parses the timetable from the MAI website with the specified parameters

    Args:
        group_number (str): number of group
    """
    config = configparser.RawConfigParser()
    config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))
    group_number = config.get('timetable', 'group_number')
    useragent = UserAgent()
    headers = {
        'Accept': '*/*',
        'User-Agent': f'{useragent.random}'
    }
    data = {'results':[]}

    url = 'https://mai.ru/education/schedule/detail.php?group=' + group_number + '&week='

    count = 1
    new_url = url + str(count)

    req = requests.get(new_url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    year = datetime.datetime.now().year

    while soup.find('span', class_='sc-day') != None:

        days = soup.find_all('div', class_='sc-table sc-table-day')

        for day in days:
            day_block = day.find(
                'div',
                class_='sc-table-col sc-day-header sc-gray'
            )
            if day_block == None:
                day_block = day.find(
                'div',
                class_='sc-table-col sc-day-header sc-blue'
            )
            day_of_week = day_block.text[-2::]

            date = day_block.text[:-2:] + f'.{year}'

            lessons_in_day = day.find('div', class_='sc-table-row').find_all('div', class_='sc-table-row')

            lessons = []
            for lesson_info in lessons_in_day:
                time_ = lesson_info.find('div', class_='sc-table-col sc-item-time').text
                type_ = lesson_info.find('div', class_='sc-table-col sc-item-type').text
                title = lesson_info.find('div', class_='sc-table-col sc-item-title').text.strip().split('\n\n')[0]
                location = lesson_info.find('div', class_='sc-table-col sc-item-location').text.strip()
                if location == '':
                    location = None
                lesson = {'time': time_, 'type': type_, 'title': title, 'location': location}
                lessons.append(lesson)
            data['results'].append({'day_of_week': day_of_week, 'date': date, 'lessons': lessons})
        if count == 1:
            break
        new_url = url + str(count)
        count += 1
        req = requests.get(new_url, headers=headers)
        soup = BeautifulSoup(req.text, 'lxml')
    return data

def add_timetable_to_db(data):
    pass

if __name__ == '__main__':
    # add_timetable_to_db(parse_timetable())
    pass