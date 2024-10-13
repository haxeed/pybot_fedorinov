import os
from dotenv import load_dotenv
import requests
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import re
import paramiko
import psycopg2
from tabulate import tabulate
import subprocess
load_dotenv()
TOKEN = (os.getenv("TOKEN"))

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

###############################################################
def start(update: Update, context):
    user = update.effective_user
    logger.info(f'Пользователь {user.username} вызвал команду /start.')
    update.message.reply_text(f'Привет {user.full_name}!')
    update.message.reply_text(f'Я умею выполнять следующие команды:\n'
                              f'/find_email - найду в тексте все электронные почты\n'
                              f'/find_phone_number - найду в тексте все номера телефона\n'
                              f'/verify_password - проверю твой пароль на прочность\n\n'
                              f'У меня также есть удаленный сервер! Могу вывести информацию и о нем:\n'
                              f'/get_release - релиз системы\n'
                              f'/get_uname - архитектура процессора, имя хоста и версия ядра\n'
                              f'/get_uptime - время работы\n'
                              f'/get_df - состояние файловой системы\n'
                              f'/get_free - состояние оперативной памяти\n'
                              f'/get_mpstat - производительность системы\n'
                              f'/get_w - работающие в системе пользователи\n'
                              f'/get_auths - последние 10 входов в систему\n'
                              f'/get_critical - последние 5 критических событий\n'
                              f'/get_ps - информация о запущенных процессах\n'
                              f'/get_ss - информация об используемых портах\n'
                              f'/get_apt_list - информация об установленных пакетах\n'
                              f'/get_services - информация о запущенных сервисах\n\n'
                              f'А еще я умею работать с базой данных! Ты можешь вносить в нее информацию после выполнения /find_email или /find_phone_number\n'
                              f' Или ты можешь посмотреть информацию в таблицах:\n'
                              f'/get_emails - данные из таблицы Emails\n'
                              f'/get_phone_numbers - данные из таблицы PhoneNumbers\n\n'
                              f'/get_repl_logs - получить логи о репликации'
                              f'Если вдруг забудешь, какие есть команды - не стесняйся, пиши "/help" :)')
    logger.info(f'Выполнение /start завершено.')
###############################################################

###############################################################
def help(update: Update, context):
    user = update.effective_user
    logger.info(f'Пользователь {user.username} вызвал команду /help.')
    update.message.reply_text(f'Я умею выполнять следующие команды:\n'
                              f'/find_email - найду в тексте все электронные почты\n'
                              f'/find_phone_number - найду в тексте все номера телефона\n'
                              f'/verify_password - проверю твой пароль на прочность\n\n'
                              f'У меня также есть удаленный сервер! Могу вывести информацию и о нем:\n'
                              f'/get_release - релиз системы\n'
                              f'/get_uname - архитектура процессора, имя хоста и версия ядра\n'
                              f'/get_uptime - время работы\n'
                              f'/get_df - состояние файловой системы\n'
                              f'/get_free - состояние оперативной памяти\n'
                              f'/get_mpstat - производительность системы\n'
                              f'/get_w - работающие в системе пользователи\n'
                              f'/get_auths - последние 10 входов в систему\n'
                              f'/get_critical - последние 5 критических событий\n'
                              f'/get_ps - информация о запущенных процессах\n'
                              f'/get_ss - информация об используемых портах\n'
                              f'/get_apt_list - информация об установленных пакетах\n'
                              f'/get_services - информация о запущенных сервисах\n\n'
                              f'А еще я умею работать с базой данных! Ты можешь вносить в нее информацию после выполнения /find_email или /find_phone_number\n'
                              f'Или ты можешь посмотреть информацию в таблицах:\n'
                              f'/get_emails - данные из таблицы Emails\n'
                              f'/get_phone_numbers - данные из таблицы PhoneNumbers\n\n'
                              f'/get_repl_logs - получить логи о репликации')
    logger.info(f'Выполнение /help завершено.')
###############################################################

###############################################################
def findEmailCommand(update: Update, context):
    user = update.effective_user
    logger.info(f'Пользователь {user.username} вызвал команду /find_email.')
    update.message.reply_text('Введите текст для поиска электронных почт: ')

    return 'find_email'

def find_email(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) электронные почты

    emailRegex = re.compile(r'[A-Za-z0-9._]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')      # регулярка под почту
    emailList = emailRegex.findall(user_input)  # Ищем электронные почты

    if not emailList:  # Обрабатываем случай, когда почт нет
        update.message.reply_text('Электронные почты не найдены')
        logger.info(f'Электронные почты не найдены.')
        return ConversationHandler.END # Завершаем выполнение функции

    emails = ''  # Создаем строку, в которую будем писать почты
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'  # Записываем очередную почту

    update.message.reply_text(emails)  # Отправляем сообщение пользователю
    logger.info(f'Найденные электронные почты: {emails}')
    logger.info(f'Выполнение /find_email завершено.')
    context.user_data['emailList'] = emailList
    # Добавление найденного в БД
    update.message.reply_text('Желаете ли вы добавить найденные записи в базу данных?\nОтветьте "+", если да\nОтветьте "-", если нет')
    return 'insert_email'

def insert_email(update: Update, context):
    user_input = update.message.text
    emailList = context.user_data.get('emailList', [])
    if (user_input == '+'):
        cursor, connection = ConnectDB()
        database = os.getenv('DB_DATABASE')
        for email in emailList:
            cursor.execute("INSERT INTO Emails (Email) VALUES (%s);", (email,))
        connection.commit()
        cursor.close()
        connection.close()
        update.message.reply_text('Найденные почты добавлены в базу данных. Для просмотра обновленной таблицы используйте /get_emails.')  # Отправляем сообщение пользователю
        logger.info(f'Добавлены записи в таблицу Emails (pybot_db)')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    elif (user_input == '-'):
        update.message.reply_text('Понял, записи добавлять не будем :)')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    else:
        update.message.reply_text('Пожалуйста, используйте "+" или "-".')
        return 'insert_email'  # Вновь запускаем функцию
###############################################################

###############################################################
def verifyPasswordCommand(update: Update, context):
    user = update.effective_user
    logger.info(f'Пользователь {user.username} вызвал команду /verify_password.')
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий пароль
    conditionsRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),\.\?]).{8,}$')      # регулярка под пароль
    spaceRegex = re.compile(r'[ \t\n]+') # регулярка для проверки пробелов/табов/новых строк
    checkSpace = spaceRegex.match(user_input) # Ищем пробелы
    if checkSpace:
        update.message.reply_text('В пароле не должно содержаться пробелов, нескольких строк или табуляций')
        return
    checkConditions = conditionsRegex.findall(user_input)  # Проверяем пароль
    if checkConditions:
        update.message.reply_text('Пароль сложный')
        logger.info(f'Выполнение /verify_password завершено. Результат: {user_input} - сложный пароль')
    else:
        update.message.reply_text('Пароль простой')
        logger.info(f'Выполнение /verify_password завершено. Результат: {user_input} - простой пароль')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
###############################################################
def findPhoneNumbersCommand(update: Update, context):
    user = update.effective_user
    logger.info(f'Пользователь {user.username} вызвал команду /find_phone_number.')
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'


def find_phone_number(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:8|\+7)-? ?\(?\d{3}\)?-? ?\d{3}-? ?\d{2}-? ?\d{2}')      # принимаемый формат:
                                                                                            # 8 (000) 000-00-00
                                                                                            # 8-000-000-00-00
                                                                                            # 8(000)0000000
                                                                                            # 800000000
                                                                                            # 8 (000) 000 00 00
                                                                                            # 8-(000)-000-00-00
                                                                                            # '+7' = '8'
    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  ConversationHandler.END# Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    logger.info(f'Выполнение /find_phone_number завершено. Найденные номера: {phoneNumbers}')
    context.user_data['phoneNumberList'] = phoneNumberList
    # Добавление найденного в БД
    update.message.reply_text('Желаете ли вы добавить найденные записи в базу данных?\nОтветьте "+", если да\nОтветьте "-", если нет')

    return 'insert_phone_number'

def insert_phone_number(update: Update, context):
    user_input = update.message.text
    phoneNumberList = context.user_data.get('phoneNumberList', [])
    if (user_input == '+'):
        cursor, connection = ConnectDB()
        for phone in phoneNumberList:
            cursor.execute("INSERT INTO PhoneNumbers (Phone) VALUES (%s);", (phone,))
        connection.commit()
        cursor.close()
        connection.close()
        update.message.reply_text('Найденные номера телефонов добавлены в базу данных. Для просмотра обновленной таблицы используйте /get_phone_numbers.')  # Отправляем сообщение пользователю
        logger.info(f'Добавлены записи в таблицу PhoneNumbers (pybot_db)')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    elif (user_input == '-'):
        update.message.reply_text('Понял, записи добавлять не будем :)')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    else:
        update.message.reply_text('Пожалуйста, используйте "+" или "-".')
        return 'insert_phone_number'  # Вновь запускаем функцию
###############################################################

############################################################### подключение по SSH к обычному пользователю
def sshConnect():
    logger.info(f'Запрашивается подключение к удаленному серверу.')
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logger.info(f'Произведено подключение к удаленному серверу.')
    return client
############################################################### подключение по SSH к обычному пользователю

############################################################### get_release
def get_release(update: Update, context):
    update.message.reply_text('Информация о релизе:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда cat /etc/os-release')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_release

############################################################### get_uname
def get_uname(update: Update, context):
    update.message.reply_text('Информация об архитектуре процессора, имени хоста системы и версии ядра:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда uname -a')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_uname

############################################################### get_uptime
def get_uptime(update: Update, context):
    update.message.reply_text('Информация о времени работы:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда uptime')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_uptime

############################################################### get_df
def get_df(update: Update, context):
    update.message.reply_text('Информация о состоянии файловой системы:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда df -h')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_df

############################################################### get_free
def get_free(update: Update, context):
    update.message.reply_text('Информация о состоянии оперативной памяти:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда free -h')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_free

############################################################### get_mpstat

def get_mpstat(update: Update, context):
    update.message.reply_text('Информация о производительности:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда mpstat')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_mpstat

############################################################### get_w
def get_w(update: Update, context):
    update.message.reply_text('Информация о работающих в системе пользователях:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда w')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_w

############################################################### get_auths
def get_auths(update: Update, context):
    update.message.reply_text('Информация о последних 10 входах в систему:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда last -n 10')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_auths

############################################################### get_critical
def get_critical(update: Update, context):
    update.message.reply_text('Информация о последних 5 критических состояниях:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('sudo journalctl -p crit -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда sudo journalctl -p crit -n 5')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_critical

############################################################### get_ps
def get_ps(update: Update, context):
    update.message.reply_text('Информация о запущенных процессах:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда ps')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_ps

############################################################### get_ss
def get_ss(update: Update, context):
    update.message.reply_text('Информация об используемых портах:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('ss -tuln')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда ss -tuln')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_ss

############################################################### get_apt_list
def aptListInfo(update: Update, context):
    update.message.reply_text('Если вам необходима общая информация о всех пакетах, напишите "+". '
                              'ВНИМАНИЕ! Вывод будет отправлен вам в файле, так как он достаточно объемный.')  # Отправляем сообщение пользователю
    update.message.reply_text('Если же вам необходима информация о каком-то конкретном пакете, напишите его название. Например: "openssh-client".')  # Отправляем сообщение пользователю
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user = update.effective_user
    user_input = update.message.text  # Получаем ответ пользователя ("+" или название пакета)
    client = sshConnect()
    if (user_input == '+'):
        stdin, stdout, stderr = client.exec_command('apt list --installed')
        data = stdout.read() + stderr.read()
        client.close()

        file_path = 'apt_list.txt'
        with open(file_path, 'w') as f:
            f.write(str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1])
        update.message.reply_document(open(file_path, 'rb'))
        os.remove(file_path)
        logger.info(f'Пользователь {user.username} получил информацию о всех установленных пакетах.'
                    f'Результат был записан в apt_list.txt, который был удален после отправки.')
    else:
        stdin, stdout, stderr = client.exec_command(f'apt show {user_input}')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        errorRegex = re.compile(r'No packages found')
        checkForPacket = errorRegex.findall(data)  # Проверяем: если пакета нет, в тексте будет Error
        if not checkForPacket:
            update.message.reply_text(data)
            logger.info(f'Пользователь {user.username} получил информацию о существующем пакете {user_input}.')
        else:
            update.message.reply_text('Пакет не найден')
            logger.info(f'Пользователь {user.username} попытался получить информацию о несуществующем пакете')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_apt_list

############################################################### get_services
def get_services(update: Update, context):
    update.message.reply_text('Информация об используемых сервисах:')  # Отправляем сообщение пользователю
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('sudo service --status-all')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)  # Отправляем сообщение пользователю
    logger.info(f'На удаленном сервере выполнена команда sudo service --status-all')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_services

############################################################### get_repl_logs
def get_repl_logs(update: Update, context):
    update.message.reply_text('Записи о репликации БД в логах:')  # Отправляем сообщение пользователю
    replData = subprocess.run(['grep', 'repl', '/app/masterlog/postgresql.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if replData.stdout:
        # Получаем последние 20 строк из вывода grep с помощью tail
        lastReplData = subprocess.run(['tail', '-n', '20'], input=replData.stdout, stdout=subprocess.PIPE, text=True)
        lastReplData = lastReplData.stdout.strip()
        update.message.reply_text(lastReplData)  # Отправляем сообщение пользователю
        logger.info(f'Изучены логи о репликации')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
    else:
        update.message.reply_text('Нет записей о репликации')  # Отправляем сообщение пользователю
        logger.info(f'Логов о репликации не было обнаружено при попытке прочтения')
        return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### подключение по SSH к пользователю БД
def ConnectDB():
    logger.info(f'Запрашивается подключение к Master DB.')
    connection = psycopg2.connect(
        host = os.getenv('DB_HOST'),  # Имя контейнера PostgreSQL или IP-адрес
        port = os.getenv('DB_PORT'),  # Порт по умолчанию для PostgreSQL
        database = os.getenv('DB_DATABASE'),  # Название вашей базы данных
        user = os.getenv('DB_USER'),  # Имя пользователя PostgreSQL
        password = os.getenv('DB_PASSWORD')  # Пароль пользователя PostgreSQL
    )

    cursor = connection.cursor()
    logger.info(f'Произведено подключение к Master DB.')
    return cursor, connection
############################################################### подключение по SSH к пользователю БД

############################################################### get_emails
def get_emails(update: Update, context):
    update.message.reply_text('Записи в таблице "Emails":')  # Отправляем сообщение пользователю
    cursor, connection = ConnectDB()
    cursor.execute("SELECT * FROM Emails;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] # Получаем имена столбцов
    data = tabulate(rows, headers=columns, tablefmt="grid")
    cursor.close()
    connection.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(f'```\n{data}\n```', parse_mode='Markdown')  # Отправляем сообщение пользователю
    logger.info(f'Получены записи из таблицы Emails (pybot_db)')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_emails

############################################################### get_phone_numbers
def get_phone_numbers(update: Update, context):
    update.message.reply_text('Записи в таблице "PhoneNumbers":')  # Отправляем сообщение пользователю
    cursor, connection = ConnectDB()
    cursor.execute("SELECT * FROM PhoneNumbers;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] # Получаем имена столбцов
    data = tabulate(rows, headers=columns, tablefmt="grid")
    cursor.close()
    connection.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(f'```\n{data}\n```', parse_mode='Markdown')  # Отправляем сообщение пользователю
    logger.info(f'Получены записи из таблицы PhoneNumbers (pybot_db)')
    return ConversationHandler.END  # Завершаем работу обработчика диалога
############################################################### get_phone_numbers

def main():
    # Передаем токен программе обновления
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    ########################################################### ТЕЛЕФОНЧИКИ
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'insert_phone_number': [MessageHandler(Filters.text & ~Filters.command, insert_phone_number)],
        },
        fallbacks=[]
    )
    ########################################################### ТЕЛЕФОНЧИКИ

    ########################################################### ПОЧТА
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'insert_email': [MessageHandler(Filters.text & ~Filters.command, insert_email)],
        },
        fallbacks=[]
    )
    ########################################################### ПОЧТА

    ########################################################### ПАРОЛЬ
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    ########################################################### ПАРОЛЬ

    ########################################################### ПАКЕТЫ
    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', aptListInfo)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    ########################################################### ПАКЕТЫ

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))                          # Обработчик start
    dp.add_handler(CommandHandler("help", help))                            # Обработчик help
    dp.add_handler(convHandlerFindPhoneNumbers)                                      # Обработчик find_phone_number
    dp.add_handler(convHandlerFindEmails)                                            # Обработчик find_email
    dp.add_handler(convHandlerVerifyPassword)                                        # Обработчик verify_password
    dp.add_handler(CommandHandler("get_release", get_release))              # Обработчик get_release
    dp.add_handler(CommandHandler("get_uname", get_uname))                  # Обработчик get_uname
    dp.add_handler(CommandHandler("get_uptime", get_uptime))                # Обработчик get_uptime
    dp.add_handler(CommandHandler("get_df", get_df))                        # Обработчик get_df
    dp.add_handler(CommandHandler("get_free", get_free))                    # Обработчик get_free
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))                # Обработчик get_mpstat
    dp.add_handler(CommandHandler("get_w", get_w))                          # Обработчик get_w
    dp.add_handler(CommandHandler("get_auths", get_auths))                  # Обработчик get_auths
    dp.add_handler(CommandHandler("get_critical", get_critical))            # Обработчик get_critical
    dp.add_handler(CommandHandler("get_ps", get_ps))                        # Обработчик get_ps
    dp.add_handler(CommandHandler("get_ss", get_ss))                        # Обработчик get_ss
    dp.add_handler(convHandlerAptList)                                               # Обработчик get_apt_list
    dp.add_handler(CommandHandler("get_services", get_services))            # Обработчик get_services
    dp.add_handler(CommandHandler("get_emails", get_emails))                # Обработчик get_emails
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))  # Обработчик get_phone_numbers
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))          # Обработчик get_repl_logs
    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()

