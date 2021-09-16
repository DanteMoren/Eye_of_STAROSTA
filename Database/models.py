from peewee import *

db = SqliteDatabase('./Database/~/database.db')


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
        column_name='date',
        model=Day,
        to_field='date'
    )
    lesson_title = TextField()
    lesson_time = TextField()
    lesson_type = CharField()
    homework = TextField(
        null=True
    )
    location = TextField(
        null=True
    )

    class Meta:
        db_table = 'Homeworks'
        primary_key = CompositeKey('day', 'lesson_title', 'lesson_time')


def add_day(data):
    """add day and lessons in database

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
                            'location': None
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
        day = Day.create(
            date=data.get('date'),
            day_of_week=data.get('day_of_week'),
            homework=False
        )
        for lesson in data.get('lessons'):
            Homework.create(
                day=day,
                lesson_title=lesson.get('title'),
                lesson_time=lesson.get('time'),
                lesson_type=lesson.get('type'),
                homework=None,
                location=lesson.get('location')
            )
    except IntegrityError:
        day = Day.get(
            date=data.get('date'),
            day_of_week=data.get('day_of_week')
        )
        update_day(day, data)
    except Exception as e:
        print(e)

# TODO понять как обновлять эту хуйню


def update_day(day, data):
    day = Day.get(
        date=data.get('date'),
        day_of_week=data.get('day_of_week')
    )
    for lesson in data.get('lessons'):
        homework = Homework.update(
            {
                Homework.lesson_type: 'test',
                Homework.homework: None,
                Homework.location: lesson.get('location')
            }
        ).where(Homework.date == day.date)
        homework.execute()
    print('запись обновлена')


def add_homework(data):
    pass


if __name__ == '__main__':
    with db:
        db.drop_tables([Day, Homework])
        db.create_tables([Day, Homework])
