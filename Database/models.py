from peewee import *
import configparser
import codecs
import os
import time
import datetime

config = configparser.RawConfigParser()
config.read_file(codecs.open(os.path.abspath('config.cfg'), "r", "utf8"))

db_dir = config.get('database', 'dir')

db = SqliteDatabase(db_dir)

class BaseModel(Model):

    class Meta:
        database = db


class CoupleTime(BaseModel):
    couple_number = PrimaryKeyField()
    couple_start = TimeField(
        formats='%H:%M'
    )
    couple_end = TimeField(
        formats='%H:%M'
    )

    class Meta:
        db_table = 'CoupleTimes'


class Subject(BaseModel):
    subject_title = CharField()

    couple_type = CharField()

    teacher = CharField(
        null=True
    )

    location = TextField(
        null=True
    )

    class Meta:
        db_table = 'Subjects'
        primary_key = CompositeKey('subject_title', 'couple_type')


class Day(BaseModel):
    date = DateField(
        formats='%Y-%m-%d'
    )

    day_of_week = CharField()

    couple_number = ForeignKeyField(
        model=CoupleTime,
        to_field='couple_number',
        column_name='couple_number'
    )

    subject_title = ForeignKeyField(
        model=Subject,
        to_field='subject_title',
        column_name='subject_title'
    )

    couple_type = ForeignKeyField(
        model=Subject,
        to_field='couple_type',
        column_name='couple_type'
    )

    homework = TextField(
        null=True,
        default=None
    )

    class Meta:
        db_table = 'Days'
        primary_key = CompositeKey('date', 'couple_number')


class File(BaseModel):
    file_name = CharField(
        primary_key=True
    )

    verbose_name = TextField(
        null=True
    )

    homework = ForeignKeyField(
        model=Day,
        to_field='homework',
        column_name='homework'
    )

    subject_title = CharField(
        null=True
    )

    link = TextField()

    class Meta:
        db_table = 'Files'


def convert_str_to_time(str_time):
    time_ = time.strftime('%H:%M', time.strptime(str_time, '%H:%M'))
    return(time_)


def create_or_update_subject(title, type, teacher=None, location=None):
    subject = Subject.get_or_create(subject_title=title, couple_type=type)
    if teacher is None:
        teacher = subject[0].teacher
    if location is None:
        location = subject[0].location
    updated_subject = Subject.update(
        teacher=teacher,
        location=location
        ).where(Subject.subject_title==title, Subject.couple_type==type)
    updated_subject.execute()
    return(subject)


def create_or_update_day(date, day_of_week, couple_number, subject_title, couple_type, home):
    day = Day.get_or_create(date, day_of_week, couple_number, subject_title, couple_type)


def add_day(data):
    """add day and lesson in database

    Args:
        data (dict):
                {
                    'day_of_week': 'Ср',
                    'date': '01.09.2021',
                    'lessons': [
                        {
                            'time': '10:45 – 12:15',
                            'type': 'ПЗ ',
                            'title': 'Физическая культура (спортивные секции)',
                            'location': None,
                            'teacher': None
                        },
                        {
                            'time': '14:45 – 16:15',
                            'type': 'ПЗ ',
                            'title': 'Иностранный язык',
                            'location': 'LMS'
                        }]
                }
    """

    try:
        lessons = data.get('lessons')
        for lesson in lessons:
            subject = create_or_update_subject(lesson.get('title'), lesson.get('type'), lesson.get('teacher'), lesson.get('location'))
            couple_start = lesson.get('time').split(' – ')[0]
            couple_start_time = convert_str_to_time(couple_start)
            Day.create(
                date=datetime.datetime.strptime(data.get('date'), '%d.%m.%Y').date(),
                day_of_week=data.get('day_of_week'),
                couple_number=CoupleTime.select().where(
                    CoupleTime.couple_start==couple_start_time).get(),
                subject_title=subject[0].subject_title,
                couple_type=subject[0].couple_type,
            )
    except Exception as e:
        print(e)

# ! TODO понять как обновлять эту хуйню


# def update_day(day, data):
#     day = Day.get(
#         date=data.get('date'),
#         day_of_week=data.get('day_of_week')
#     )
#     for lesson in data.get('lessons'):
#         homework = Homework.update(
#             {
#                 Homework.lesson_type: 'test',
#                 Homework.homework: None,
#                 Homework.location: lesson.get('location')
#             }
#         ).where(Homework.date == day.date)
#         homework.execute()
#     print('запись обновлена')


def add_homework(data):
    pass


if __name__ == '__main__':
    with db:
        db.drop_tables([Day, CoupleTime, Subject, File])
        db.create_tables([Day, CoupleTime, Subject, File])

    for i in range(1,7):
        start_time = convert_str_to_time(config.get('couple_time', str(i)+'_start'))
        end_time = convert_str_to_time(config.get('couple_time', str(i)+'_end'))
        CoupleTime.create(
            couple_number = i,
            couple_start = start_time,
            couple_end = end_time
        )
    # data = {
    #                 "day_of_week": "Вт",
    #     "date": "21.09.2021",
    #     "lessons": [
    #         {
    #             "time": "09:00 – 10:30",
    #             "type": "ЛК",
    #             "title": "Военная подготовка",
    #             "location": "ПЛАЦ",
    #             "teacher": 'МАРСЕЛЬ'
    #         },]
    #             }
    # add_day(data)
