import peewee
import os
from dotenv import load_dotenv

load_dotenv()

SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_HOST = os.getenv('SQL_HOST')
SQL_USER = os.getenv('SQL_USER')
SQL_DB_NAME = os.getenv('SQL_DB_NAME')
SQL_PORT = int(os.getenv('SQL_PORT'))

try:
    with peewee.MySQLDatabase(
        'timetable',
        user=SQL_USER,
        password=SQL_PASSWORD,
        host=SQL_HOST,
        port=SQL_PORT
    ) as connection:
        cursor = connection.cursor()
except Exception as e:
    raise Exception


class BaseModel(peewee.Model):
    class Meta:
        database = connection


class Day(BaseModel):
    day_of_week = peewee.TextField(
        column_name='Day_of_week',
        null=True
    )
    date = peewee.CharField(
        primary_key=True,
        column_name='Date',
        null=False
    )
    homework = peewee.BooleanField(
        column_name='Homework',
        null=True,
        default=False
    )


class Homework(BaseModel):
    day = peewee.ForeignKeyField(
        model=Day,
        related_name='Date',
        null=False
    )
    lesson = peewee.TextField(
        column_name='Lesson',
        null=False
    )
    homework = peewee.TextField(
        column_name='Homework',
        null=True,
    )
    Location = peewee.TextField(
        column_name='Location',
        null=True
    )

    class Meta:
        constraints = [peewee.SQL('UNIQUE (date, lesson)')]

Homework.create_table()
Day.create_table()