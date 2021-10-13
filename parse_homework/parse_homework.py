import configparser
import os
import requests
from fake_useragent import UserAgent
import codecs
from dotenv import load_dotenv

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


    posts = req.json()
    print(posts)
    # for post in posts:
    #     print(post)
        # if '#ДЗ@m3o_19bk_19' in post.get('text'):
        #     print(post.get('text'))
    # with codecs.open('vk_page.json', 'w', "utf-8") as file:
    #     file.write(req.text)

def add_homework(data):
    pass


if __name__ == '__main__':
    parse_homework()