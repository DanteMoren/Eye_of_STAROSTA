import configparser
import os
import codecs
import requests
import datetime
import sys
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

sys.path.insert(0, "/opt/database")

from models import add_day


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
    data = []

    url = ('https://mai.ru/education/schedule/detail.php?group='
           + group_number +
           '&week=')

    count = 1
    new_url = url + str(count)

    req = requests.get(new_url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    year = datetime.datetime.now().year

    while soup.find('span', class_='sc-day') is not None:
        print('...')
        days = soup.find_all('div', class_='sc-table sc-table-day')

        for day in days:
            day_block = day.find(
                'div',
                class_='sc-table-col sc-day-header sc-gray'
            )
            if day_block is None:
                day_block = day.find(
                    'div',
                    class_='sc-table-col sc-day-header sc-blue'
                )
            day_of_week = day_block.text[-2::]

            date = day_block.text[:-2:] + f'.{year}'

            lessons_in_day = day.find(
                'div',
                class_='sc-table-row'
            ).find_all('div', class_='sc-table-row')

            lessons = []

            for lesson_info in lessons_in_day:
                time_ = lesson_info.find(
                    'div',
                    class_='sc-table-col sc-item-time'
                ).text

                type_ = lesson_info.find(
                    'div',
                    class_='sc-table-col sc-item-type'
                ).text.strip()

                title = lesson_info.find(
                    'div',
                    class_='sc-table-col sc-item-title'
                ).text.strip().split('\n\n')[0]

                location = lesson_info.find_all(
                    'div',
                    class_='sc-table-col sc-item-location'
                )[1].text.strip()

                if location == '':
                    location = None
                lesson = {
                              'time': time_,
                              'type': type_,
                              'title': title,
                              'location': location,
                              'teacher': None
                    }
                lessons.append(lesson)
            print(date)
            data.append(
                {
                    'day_of_week': day_of_week,
                    'date': date,
                    'lessons': lessons
                    }
            )
        # if count == 3:
        #     break
        count += 1
        new_url = url + str(count)
        req = requests.get(new_url, headers=headers)
        soup = BeautifulSoup(req.text, 'lxml')
    with open('parse_timetable/timetable.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return data


def add_timetable_to_db(data):
    for day in data:
        add_day(day)


if __name__ == '__main__':
    with open('parse_timetable/timetable.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    add_timetable_to_db(data)
