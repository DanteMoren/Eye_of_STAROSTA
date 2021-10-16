import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Database.models import *
from parse_timetable.parse_timetable import add_timetable_to_db
from parse_homework.parse_homework import parse_homework

if __name__ == '__main__':
    with db:
        db.drop_tables([Day, CoupleTime, Subject, File])
        db.create_tables([Day, CoupleTime, Subject, File])

    for i in range(1, 7):
        start_time = convert_str_to_time(
            config.get('couple_time', str(i)+'_start'))
        end_time = convert_str_to_time(
            config.get('couple_time', str(i)+'_end'))
        CoupleTime.create(
            couple_number=i,
            couple_start=start_time,
            couple_end=end_time
        )
    
    with open('parse_timetable/timetable.json', 'r', encoding='utf-8') as file:
        timetable_data = json.load(file)
    add_timetable_to_db(timetable_data)

    homework_data = parse_homework()
    for homework in homework_data:
        add_homework(homework)