import sys
import requests
import json
import os.path

if os.path.isfile("trello_user.txt"):
    print ("Файл авторизации существует")

    file_object = open("trello_user.txt")
    user = json.load(file_object)
    file_object.close()

    base_url = "https://api.trello.com/1/{}"
    auth_params = {
        'key': user['key'],
        'token': user['token'], }
    board_long_id = user['board_long_id']


else:
    print ("Ваши данные.")
    base_url = "https://api.trello.com/1/{}"
    key = input("Введите key Trello: ")
    token = input("Введите token Trello: ")
    board = input("Введите board_id доски Trello: ")
    auth_params = {
        'key': key,
        'token': token, }
    board_id = board

    response = requests.get(base_url.format('boards/' + board_id), params=auth_params).json()
    board_long_id = response['id']
    print('board_long_id {}'.format(board_long_id))

    # создаем словарь с данными пользователя
    user = {"key": key, "token": token, "board_long_id": board_long_id, }
    # открываем на запись файл user.txt
    file_object = open("trello_user.txt", "w")
    # сохраняем словарь user в объект файла file_object
    json.dump(user, file_object)
    # закрываем объект файла
    file_object.close()

    print('Файл авторизации trello_user.txt создан. Авторизация в дальнейшем не потребуется!')


def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_long_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        #print(column['name'])
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(column['name'] + " - ({})".format(len(task_data)))

        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'] + '\t' + task['id'])
    print('Функции: create(name, column_name) - создать, move(name, column_name) - переместить')
    print('Используйте терминал (python trello.py create "New task" "To Do")')

def create(name, column_name):
    column_id = column_check(column_name)
    if column_id is None:
        column_id = create_column(column_name)['id']

    requests.post(base_url.format('cards'), data={'name': name, 'idList': column_id, **auth_params})

def move(name, column_name):
    duplicate_tasks = get_task_duplicates(name)
    if len(duplicate_tasks) > 1:
        print("Задач с таким названием несколько:")
        for index, task in enumerate(duplicate_tasks):
            task_column_name = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']
            print("Задача №{}\tid: {}\tНаходится в колонке: {}\t ".format(index, task['id'], task_column_name))
        task_id = input("Введите ID задачи, которую нужно переместить: ")
    else:
        task_id = duplicate_tasks[0]['id']
    if column_id is None:
        column_id = create_column(column_name)['id']
    requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_id, **auth_params})

def column_check(column_name):
    column_data = requests.get(base_url.format('boards') + '/' + board_long_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == column_name:
            return column['id']
    return

def create_column(column_name):
    return requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_long_id, **auth_params}).json()

    def get_task_duplicates(task_name):
        column_data = requests.get(base_url.format('boards') + '/' + board_long_id + '/lists', params=auth_params).json()
        duplicate_tasks = []
        for column in column_data:
            column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
            for task in column_tasks:
                if task['name'] == task_name:
                    duplicate_tasks.append(task)
    return duplicate_tasks





if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
