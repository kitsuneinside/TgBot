from bot_info import *
from DB import *
import random
import string
from datetime import datetime
import os
from Markup import *

folder_name = "photo_folder"

current_directory = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(current_directory, "photo_folder")



def name_generation(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#work with planed message


@bot.message_handler(commands=['planed_message_bar'])
def planed_message_barr(message):
    bot.send_message(message.chat.id, 'Обери що бажаєш редагувати', reply_markup=adminmarkupp)


@bot.message_handler(commands=['action_bar'])
def action_barr(message):
    bot.send_message(message.chat.id, 'Обери що бажаєш редагувати', reply_markup=adminmarkupp2)


@bot.message_handler(commands=['send_messages_from_users'])
def send_name_event(message):
    bot.send_message(message.chat.id, 'Надішліть назву запланованого повідомлення яке має бути відправлене ')
    bot.register_next_step_handler(message, send_messages)
def send_messages(message):
    with db:
        for mess in Message.select():
            if mess.name == message.text:
                file_path = mess.image_data
                textt = mess.text_message

        for usid in User.select():
            try:
                with open(os.path.join(path, f"{file_path}.jpg"), 'rb') as photo:
                    bot.send_photo(usid.id, photo, caption=textt)

            except:
                bot.send_message(usid.id, textt)


@bot.message_handler(commands=['event_list'])
def select_all_from_db(message):
   with db:
       for mess in Message.select():
           try:
               with open(os.path.join(path, f"{mess.image_data}.jpg"), 'rb') as photo:
                   bot.send_photo(message.chat.id, photo, caption=f'name: {mess.name}\n'
                                                                  f'text: {mess.text_message}\n'
                                                                  f'date: {mess.date}\n')
           except:
               bot.send_message(message.chat.id, f'name: {mess.name}\n'
                                                 f'text: {mess.text_message}\n'
                                                 f'date: {mess.date}\n')


@bot.message_handler(commands = ['add_events'])

def tmp(message):
    bot.send_message(message.chat.id, 'Надішліть назву для запланованого повідомлення')
    bot.register_next_step_handler(message, insert_photo_in_db)

def insert_photo_in_db(message):
   event_name = message.text
   bot.send_message(message.chat.id, 'Надішліть фото для запланованого повідомлення, або відправте будь-який текст, '
                                     'щоб пропустити цей крок')
   bot.register_next_step_handler(message, download_image, event_name)
def download_image(message, event_name):
    if message.photo:

        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Створено папку {folder_name}")
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        event_photo = f'{name_generation()}'

        with open(os.path.join(path, f"{event_photo}.jpg"), 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.register_next_step_handler(message, insert_in_db, event_name, event_photo)
        bot.send_message(message.chat.id, "Надішліть текст для запланованого повідомлення")
    else :
        bot.register_next_step_handler(message, insert_in_db, event_name)
        bot.send_message(message.chat.id, "Надішліть текст для запланованого повідомлення")
def insert_in_db(message, event_name, event_photo = 'DEFAULT'):
    with db:
        Message.create(name=f'{event_name}', text_message=message.text, date=datetime.now(), image_data=f'{event_photo}')
        bot.send_message(message.chat.id, 'Заплановане повідомлення добавлене в базу даних')


@bot.message_handler(commands=['edit_event'])
def chose_edit(message):
    bot.send_message(message.chat.id, 'Обери що бажаєш змінити', reply_markup=edit_markup)


@bot.message_handler(commands=['edit_text'])
def name_edit_t(message):
    bot.register_next_step_handler(message, edit_t)
    bot.send_message(message.chat.id,'Надішліть назву повідомлення в якому бажаєте замінти текст')

def edit_t(message):
    try:
        with db.atomic():
            message_record = Message.get(Message.name == message.text)
            bot.send_message(message.chat.id, message_record.text_message)
            bot.register_next_step_handler(message, lambda m: insert_edit_txt(m, message_record))
    except Message.DoesNotExist:
        bot.send_message(message.chat.id, f"Подія з назвою '{message.text}' не знайдена.")
def insert_edit_txt(message, db_record):
    with db.atomic():
        db_record.text_message = message.text
        db_record.save()
    bot.send_message(message.chat.id, "Текст оновлено успішно!")



@bot.message_handler(commands=['edit_photos'])
def name_edit_p(message):
    bot.register_next_step_handler(message, edit_photo)
    bot.send_message(message.chat.id, 'Надішліть назву повідомлення в якому бажаєте замінти фото')
def edit_photo(message):

    try:
        with db.atomic():
            for mess in Message.select():
                if mess.name == message.text:
                   photo_data = mess.image_data

            with open(os.path.join(path, f"{photo_data}.jpg"), 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
                bot.send_message(message.chat.id, 'Фото яке використовується на даний момент')

            bot.register_next_step_handler(message, lambda m: download_for_edit_image(m, photo_data))
            bot.send_message(message.chat.id, 'Надішліть фото на яке бажаєте замінити')

    except Message.DoesNotExist:
        bot.send_message(message.chat.id, f"фото з назвою '{message.text}' не знайдена.")

def download_for_edit_image(message, event_name):
    if message.photo:
        if not os.path.exists(path):
            os.makedirs(path)

        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        event_photo = f'{name_generation()}'

        with open(os.path.join(path, f"{event_photo}.jpg"), 'wb') as new_file:
            new_file.write(downloaded_file)
        with db.atomic():
            for mess in Message:
                if mess.image_data == event_name:
                    print(f'{mess.image_data}')
                    mess.image_data = f'{event_photo}'
                    print(f'{event_photo}')
                    mess.save()


@bot.message_handler(commands=['delete_event'])
def take_name(message):
    bot.send_message(message.chat.id, 'Надішліть назву запланованого повідомлення')
    bot.register_next_step_handler(message, delete_from_db)


def delete_from_db(message):
    with db:
        for mes in Message.select():
            if mes.name == message.text:
                mes.delete_instance()



#work with action


@bot.message_handler(commands = ['add_action'])
def add_action_(message):
    bot.send_message(message.chat.id, 'Надішліть назву акції')
    bot.register_next_step_handler(message, insert_photo_in_db_action)

def insert_photo_in_db_action(message):
   event_name = message.text
   bot.send_message(message.chat.id, 'Надішліть фото для акції, або відправте будь-який текст, '
                                     'щоб пропустити цей крок')
   bot.register_next_step_handler(message, download_image_for_action, event_name)
def download_image_for_action(message, action_name):
    if message.photo:

        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Створено папку {folder_name}")
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        action_photo = f'{name_generation()}'

        with open(os.path.join(path, f"{action_photo}.jpg"), 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.register_next_step_handler(message, insert_action_in_db, action_name, action_photo)
        bot.send_message(message.chat.id, "Надішліть текст для акції")
    else :
        bot.register_next_step_handler(message, insert_action_in_db, action_name )
        bot.send_message(message.chat.id, "Надішліть текст для акції")
def insert_action_in_db(message, action_name, action_photo = 'DEFAULT'):
    with db:
        Actions.create(name=f'{action_name}', text_action=message.text, date=datetime.now(), image_data=f'{action_photo}')
        bot.send_message(message.chat.id, 'Акція добавлена в базу даних')


@bot.message_handler(commands=['action_list'])
def select_all_action_from_db(message):
   with db:
       for mess in Actions.select():
           try:
               with open(os.path.join(path, f"{mess.image_data}.jpg"), 'rb') as photo:
                   bot.send_photo(message.chat.id, photo, caption=f'name: {mess.name}\n'
                                                                  f'text: {mess.text_action}\n'
                                                                  f'date: {mess.date}\n')
           except:
               bot.send_message(message.chat.id, f'name: {mess.name}\n'
                                                 f'text: {mess.text_action}\n'
                                                 f'date: {mess.date}\n')


@bot.message_handler(commands=['delete_action'])
def take_name_action_(message):
    bot.send_message(message.chat.id, 'Надішліть назву акції')
    bot.register_next_step_handler(message, delete_action_from_db)


def delete_action_from_db(message):
    with db:
        for mes in Actions.select():
            if mes.name == message.text:
                mes.delete_instance()



@bot.message_handler(commands=['edit_action'])
def chose_action_for_edit(message):
    bot.send_message(message.chat.id, 'Обери що бажаєш змінити', reply_markup=edit_action_markup)


@bot.message_handler(commands=['edit_text_action'])
def name_edit_t_action(message):
    bot.register_next_step_handler(message, edit_t_in_action)
    bot.send_message(message.chat.id,'Надішліть назву акції в якій бажаєте замінти текст')

def edit_t_in_action(message):
    try:
        with db.atomic():
            message_record = Actions.get(Actions.name == message.text)
            bot.send_message(message.chat.id, message_record.text_action)
            bot.register_next_step_handler(message, lambda m: insert_edit_txt_in_action(m, message_record))
    except Message.DoesNotExist:
        bot.send_message(message.chat.id, f"Подія з назвою '{message.text}' не знайдена.")
def insert_edit_txt_in_action(message, db_record):
    with db.atomic():
        db_record.text_action = message.text
        db_record.save()
    bot.send_message(message.chat.id, "Текст оновлено успішно!")



@bot.message_handler(commands=['edit_photos_action'])
def name_edit_p_in_action(message):
    bot.register_next_step_handler(message, edit_photo_action)
    bot.send_message(message.chat.id, 'Надішліть назву акції в якій бажаєте замінти фото')
def edit_photo_action(message):

    try:
        with db.atomic():
            for mess in Actions.select():
                if mess.name == message.text:
                   photo_data = mess.image_data

            with open(os.path.join(path, f"{photo_data}.jpg"), 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
                bot.send_message(message.chat.id,'Фото яке використовується на даний момент')

            bot.register_next_step_handler(message, lambda m: download_for_edit_image_action(m, photo_data))
            bot.send_message(message.chat.id, 'Надішліть фото на яке бажаєте замінити')

    except Message.DoesNotExist:
        bot.send_message(message.chat.id, f"фото з назвою '{message.text}' не знайдена.")

def download_for_edit_image_action(message,event_name):
    if message.photo:
        if not os.path.exists(path):
            os.makedirs(path)

        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        event_photo = f'{name_generation()}'

        with open(os.path.join(path, f"{event_photo}.jpg"), 'wb') as new_file:
            new_file.write(downloaded_file)
        with db.atomic():
            for mess in Actions:
                if mess.image_data == event_name:
                    print(f'{mess.image_data}')
                    mess.image_data = f'{event_photo}'
                    print(f'{event_photo}')
                    mess.save()
