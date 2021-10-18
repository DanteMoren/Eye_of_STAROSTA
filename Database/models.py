from re import sub
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
        field='couple_number',
        to_field='couple_number',
        column_name='couple_number'
    )

    subject_title = CharField(
        column_name='subject_title'
    )

    couple_type = CharField(
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
        null=True,
        default=None
    )

    homework_date = DateField(
        formats='%Y-%m-%d',
        null=True,
        default=None
    )

    subject_title = CharField(
        null=True,
        default=None
    )

    couple_type = CharField(
        null=True,
        default=None
    )

    link = TextField()

    class Meta:
        db_table = 'Files'


def convert_str_to_time(str_time):
    time_ = time.strftime('%H:%M', time.strptime(str_time, '%H:%M'))
    return(time_)


def convert_date(date):
    if type(date) is str:
        try:
            date = datetime.datetime.strptime(
                date, '%d.%m.%Y').date()
            return date
        except:
            date = datetime.datetime.strptime(
                date, '%Y-%m-%d').date()
            return date
    if type(date) == datetime.datetime:
        return date.date()
    print('SOME ERROR')  # TODO припилить логи


def create_or_update_subject(title, type, teacher=None, location=None):
    subject = Subject.get_or_create(subject_title=title, couple_type=type)
    if teacher is None:
        teacher = subject[0].teacher
    if location is None:
        location = subject[0].location
    updated_subject = Subject.update(
        teacher=teacher,
        location=location
    ).where(Subject.subject_title == title, Subject.couple_type == type)
    updated_subject.execute()
    subject = Subject.get(Subject.subject_title == title,
                          Subject.couple_type == type)
    return(subject)


def create_or_update_day(date, day_of_week, couple_number, subject_title, couple_type, homework=None):
    try:
        day = Day.get_or_create(
            date=date,
            day_of_week=day_of_week,
            couple_number=couple_number,
            subject_title=subject_title,
            couple_type=couple_type
        )
    except Exception as e:
        print(e)
    if homework is None:
        homework = day[0].homework
    updated_day = Day.update(
        homework=homework
    ).where(Day.date == date, Day.couple_number == couple_number)
    updated_day.execute()
    day = Day.get(
        Day.date == date,
        Day.day_of_week == day_of_week,
        Day.couple_number == couple_number,
        Day.subject_title == subject_title,
        Day.couple_type == couple_type
    )
    return day


def add_day(data):
    """add day and lesson in database

    Args:
        data (dict):
                {
                    'day_of_week': 'Ср',
                    'date': '01.09.2021',
                    'lessons': 
                    [
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
                        }
                    ]
                }
    """

    try:
        lessons = data.get('lessons')
        for lesson in lessons:
            subject = create_or_update_subject(lesson.get('title'), lesson.get(
                'type'), lesson.get('teacher'), lesson.get('location'))
            couple_start = lesson.get('time').split(' – ')[0]
            couple_start_time = convert_str_to_time(couple_start)
            create_or_update_day(
                date=datetime.datetime.strptime(
                    data.get('date'), '%d.%m.%Y').date(),
                day_of_week=data.get('day_of_week'),
                couple_number=CoupleTime.select().where(
                    CoupleTime.couple_start == couple_start_time).get(),
                subject_title=subject.subject_title,
                couple_type=subject.couple_type,
            )
    except Exception as e:
        print(e)


def add_file(file_name, link, verbose_name=None, homework_date=None, subject_title=None, couple_type=None):
    homework_date = convert_date(homework_date)
    try:
        file = File.get_or_create(
            file_name=file_name,
            link=link
        )
        if verbose_name is None:
            verbose_name = file[0].verbose_name
        if homework_date is None:
            homework_date = file[0].homework_date
        if subject_title is None:
            subject_title = file[0].subject_title
        if couple_type is None:
            couple_type = file[0].couple_type
        updated_file = File.update(
            verbose_name=verbose_name,
            homework_date=homework_date,
            subject_title=subject_title,
            couple_type=couple_type
        ).where(File.file_name == file_name, File.link == link)
        updated_file.execute()
        file = File.get(File.file_name == file_name, File.link == link)

        return file
    except Exception as e:
        print('file already exist')


def add_homework(data):
    """add homework to database

    Args:
        data (dict):
        {
            "files": 
                [
                    {
                        "name": "Задание на семинар №1.doc",
                        "link": "https://vk.com/doc316529256"
                    }
                ],
            "title": "Социология",
            "type": "ПЗ",
            "homework": "1. Астахов\n2. Альбиков\n3. Черкашин\n4. Мухамедшинов\n5. Колодяжный",
            "date": "25.09.2021"
        }
    """

    try:
        date = convert_date(data.get('date'))
        homework = data['homework']
        subject_title = data['title']
        couple_type = data['type']
        day = Day.select().where(
            Day.date == date,
            Day.subject_title == subject_title,
            Day.couple_type == couple_type).get()
        day_of_week = day.day_of_week
        couple_number = day.couple_number
        create_or_update_day(date, day_of_week, couple_number,
                             subject_title, couple_type, homework)
        for file in data.get('files'):
            add_file(
                file_name=file['name'],
                link=file['link'],
                homework_date=data['date'],
                subject_title=data['title'],
                couple_type=data['type']
            )
    except Exception as e:
        print(e)


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
