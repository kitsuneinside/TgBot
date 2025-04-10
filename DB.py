from peewee import *


db = SqliteDatabase(f'.\database.db')


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    name = CharField()

    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel):

    flag = BooleanField()

    class Meta:
        db_table = 'users'


class Message(BaseModel):

    text_message = CharField()
    date = CharField()
    image_data = CharField()

    class Meta:
        db_table = 'messages'


class Actions(BaseModel):

    text_action = CharField()
    date = CharField()
    image_data = CharField()

    class Meta:
        db_table = 'actions'


if __name__ == '__main__':
    db.create_tables([Actions])
    db.create_tables([Message])
