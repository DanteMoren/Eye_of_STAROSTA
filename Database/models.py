from peewee import *

db =  SqliteDatabase('./Database/DB/database.db')


class BaseModel(Model):

    class Meta:
        database = db


class Day(BaseModel):
    day_of_week = TextField()
    date = TextField(
        primary_key=True
    )
    homework = BooleanField(
        default=False
    )
    class Meta:
        db_table = 'Days'


class Homework(BaseModel):
    day = ForeignKeyField(
        model=Day,
        to_field='date'
    )
    lesson_title = TextField()
    lesson_time = TextField()
    lesson_type = TextField()
    homework = TextField(
        null=True
    )
    location = TextField(
        null=True
    )
    class Meta:
        db_table = 'Homeworks'
        primary_key = CompositeKey('day', 'lesson_title')

def add_day(data):
    """add day and lessons in database

    Args:
        data (dict):
                {
                    'day_of_week': 'Ср',
                    'date': '01.09.2021',
                    'lessons': [
                        {'time': '10:45 – 12:15', 'type': 'ПЗ ', 'title': 'Физическая культура (спортивные секции)', 'location': None},
                        {'time': '14:45 – 16:15', 'type': 'ПЗ ', 'title': 'Иностранный язык', 'location': 'LMS'}]
                }
    """
    try:
        day = Day.create(
            date=data.get('date'),
            day_of_week=data.get('day_of_week'),
            homework=False
        )
        for lesson in data.get('lessons'):
            Homework.create(
                day=day,
                lesson_title=lesson.get('lesson_title'),
                lesson_time=lesson.get('lesson_time'),
                lesson_type=lesson.get('lesson_type'),
                homework=None,
                location=lesson.get('location')
            )
    except:
        pass

def add_homework(data):
    pass

if __name__ == '__main__':
    with db:
        db.drop_tables([Day, Homework])
