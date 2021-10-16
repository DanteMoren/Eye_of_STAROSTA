import re
import datetime
homework_list = [
    r'(домашк\D|(^| )дз|домашн\D{2} работ\D|домашнее задание) {,1}.*\?',
    r'ч(то-то|то|е|ё).+(задали|делать|подготовить)', '(дз на)',
    r'(cк|к)инь\D{,2}.*(домашк\D|(^| )дз|домашн\D{2} работ\D|'
    r'домашнее задание) {,1}'
]

timetable_list = [
    r'(как(ая|ие)|где) пар[аы]', 'что сейчас', 'расписание',
    r'ч(то|е|ё).*завтра.*\?', r'ч(то|е|ё).*по парам', 'че завтра']

date_list = [r'\d{2}\.\d{2}\.\d{4}', r'\d{2}\.\d{2}']

next_week_list = [r'следующ\D\D недел\D', r'через недел\D']

mounth_list = [
    r'\d{2} (января|февраля|марта|апреля|мая|июня|'
    r'июля|августа|сентября|октября|ноября|декабря)'
]


mounth_dict = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

days_of_week_list = [
    r'понедельник',
    'вторник',
    r'сред[ауe]',
    'четверг',
    r'пятниц[ау]',
    r'суббот[ау]'
]

days_of_week_dict = {
    'понедельник': 0,
    'вторник': 1,
    r'сред[ауe]': 2,
    'четверг': 3,
    r'пятниц[ау]': 4,
    r'суббот[ау]': 5
}


def homework(message):
    for condition in homework_list:
        result = re.search(condition, message)
        if result:
            return True
    return False


def date(message):
    for condition in mounth_list:
        result = re.search(condition, message)
        if result:
            result = result[0].split()
            return f'{result[0]}.{mounth_dict[result[1]]}'
    for date in date_list:
        result = re.search(date, message)
        if result:
            print(result[0])
            if re.search(r'^\d{2}\.\d{2}\.\d{2}$', result[0]):
                result = result[0][:6] + '20' + result[0][6:]
                return result
            elif re.search(r'\d{2}\.\d{2}', result[0]):
                result = result[0] + '.' + str(datetime.datetime.now().year)
                return result
            return result[0]
    return False


def day_of_week(message):
    for condition in days_of_week_list:
        result = re.search(condition, message)
        if result:
            day = days_of_week_dict[condition]
            return day
    return False
    # TODO функция все крашит


def timetable(message):
    for condition in timetable_list:
        result = re.search(condition, message)
        if result:
            return True
    return False

def parse_message(message):
    message = message.lower()
    req_dict = {
        'homework': False,
        'timetable': False,
        'actual': False,
        'week': False,
        'date': False,
        'tomorrow': False,
        'today': False,
        'day_of_week': False
    }
    date_str = date(message)
    homework_bool = homework(message)
    timetable_bool = timetable(message)
    day_of_week_int = day_of_week(message)
    if homework_bool or timetable_bool:
        req_dict['homework'] = homework_bool
        req_dict['timetable'] = timetable_bool
        if day_of_week_int != False:
            req_dict['day_of_week'] = day_of_week_int
            return req_dict
        elif date_str:
            req_dict['date'] = date_str
            return req_dict
        elif re.search('завтра', message):
            req_dict['tomorrow'] = True
            return req_dict
        elif re.search('недел\D', message):
            for condition in next_week_list:
                result = re.search(condition, message)
                if result:
                    req_dict['week'] = 'next'
                    return req_dict
            req_dict['week'] = 'now'
            return req_dict
        elif re.search('сегодня', message):
            req_dict['today'] = True
            return req_dict
        else:
            req_dict['actual'] = True
            return req_dict
    else:
        return None
