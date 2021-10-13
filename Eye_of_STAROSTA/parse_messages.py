import re

homework_dict = [r'(домашк\D|дз|домашн\D{2} работ\D|домашнее задание) {,1}.*\?',
                 r'(ч(то-то|то|е|ё).+задали)',
                 r'(cк|к)инь\D{,2}.*(домашк\D|дз|домашн\D{2} работ\D|'
                 r'домашнее задание) {,1}']

date_dict = [r'\d{2}\.\d{2}\.\d{4}']
mounth_dict = []
day_of_week = []

timetable_dict = [r'']

def homework(message):
    message = message.lower()
    for condition in homework_dict:
        result = re.search(condition, message)
        if result:
            return True
    return False

def timetable(message):
    pass


if __name__ == '__main__':
    message = input()
    while message != '0':
        # message = 'какое домашнее задание?'
        if homework(message):
            print('\nТы хочешь чтобы я кинул домашку, но делаешь это без уважения.\n')
        else:
            print('\nЧе тебе надо?\n')
        message = input()
