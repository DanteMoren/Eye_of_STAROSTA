from config import m_token
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
from datetime import datetime
import random
import time

vk_session = vk_api.VkApi(token=m_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


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

    elif msg == 'расписание занятий':
        keyboard.add_button('Пары сегодня', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Расписание недели', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Ближайшие пз', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Ближайшие лабы', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Вернутся в меню', color=VkKeyboardColor.PRIMARY)

    else:
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard


def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send', {id_type: id, 'message': message, 'random_id': random.randint(
        -2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        msg = event.text.lower()
        keyboard = create_keyboard(msg)

        if event.from_user and not event.from_me:
            print('Сообщение пришло в: ' +
                  str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            print('Текст сообщения: ' + str(event.text))
            print('ID пользователя: ' + str(event.user_id))
            print('-' * 30)

            if msg == "привет" or msg == "вернутся в меню" or msg == "начать":
                send_message(vk_session, 'user_id', event.user_id,
                             message='Вас приветствует учебный бот группы М3О-19Бк-19!', keyboard=keyboard)
            elif msg == "открыть меню":
                send_message(vk_session, 'user_id', event.user_id,
                             message='Учебное меню', keyboard=keyboard)
            elif msg == 'расписание занятий':
                send_message(vk_session, 'user_id', event.user_id,
                             message='.', keyboard=keyboard)
            elif msg == 'вырубить бота нахуй':
                send_message(vk_session, 'user_id', event.user_id,
                             message='ВЫРУБАЮСЬ НАХУЙ!')
                exit(-1)

        elif event.from_chat:
            if msg == "привет":
                send_message(vk_session, 'chat_id',
                             event.chat_id, message='Привет!')
# '''
# req_dict = {
#     'week': None or 'now' or 'next',
#     'date': None or '25.09.21 etc.',
#     'today': None or True
# }
# '''
# req_dict = {
#     'week': False,
#     'date': False,
#     'today': True
# }

# def get_timetable_by_week(req_data):
#     """Get timetable by week from html req_data

#     Args:
#         req_data (str): Beautifulsoup
#     """
#     pass

# def get_timetable_by_date(req_data):
#     """Get timetable by date from html req_data

#     Args:
#         req_data (str): Beautifulsoup
#     """
#     pass

# def get_timetable_today(req_data):
#     pass

# def get_timetable_by_next_week(req_data):
#     pass
# """
