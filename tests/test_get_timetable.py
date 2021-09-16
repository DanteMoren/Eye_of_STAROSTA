import requests
import configparser
import os
import codecs
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

useragent = UserAgent()
headers ={
    'Accept': '*/*',
    f'User-Agent': '{useragent.random}'
}

URL = 'https://mai.ru/education/schedule/detail.php?group='

class TestTimetableParser:

    def test_00_group_existing(self):
        config = configparser.RawConfigParser()
        config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))
        group_number = config.get('timetable', 'group_number')
        url = URL + group_number
        req = requests.get(url, headers=headers)

        assert req.status_code == 200, ('Connectinon error')

        soup = BeautifulSoup(req.text, 'lxml')
        day = soup.find('span', class_='sc-day')
        
        assert day != None, ('The written group does not exist, check group_number in config.cfg')
