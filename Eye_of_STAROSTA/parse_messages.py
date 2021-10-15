import re
homework_list = [
    r'(домашк\D|(^| )дз|домашн\D{2} работ\D|домашнее задание) {,1}.*\?',
    r'(ч(то-то|то|е|ё).+задали)|(дз на)',
    r'(cк|к)инь\D{,2}.*(домашк\D|(^| )дз|домашн\D{2} работ\D|'
    r'домашнее задание) {,1}'
]

timetable_dict = [r'(какая|где) пара']

date_list = [r'\d{2}\.\d{2}\.\d{4}', r'\d{2}\.\d{2}']

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

day_of_week = [
    r'(понедельник|вторник|четверг|пятниц[ау]|суббот[ау]|воскресенье)'
]


def homework(message):
    message = message.lower()
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
            return result[0]
    return 0

    
def timetable(message):
    pass


if __name__ == '__main__':
    message = input()
    while message != '0':
        date_str = date(message)
        homework_bool = homework(message)
        message = 'какое домашнее задание?'
        if homework_bool and date_str:
            print(f'\nТы хочешь чтобы я кинул домашку на {date_str}, но делаешь это без уважения.\n')
        elif homework_bool:
            print(f'\nТы хочешь чтобы я кинул домашку, но делаешь это без уважения.\n')
        else:
            print('\nЧе тебе надо?\n')
        message = input()
