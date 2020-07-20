import requests
import sys
from trello import TrelloApi

auth_params = {
    'key': "a4c32f147bafe6f364adff84ba5e45bf",
    'token': "9b97661601bc533d9d8607efc49fbc9f86a3d9a7dd86ef347da404de40fea858", }
base_url = "https://api.trello.com/1/{}"
# trello = TrelloApi(apiKey, token)
# response = trello.boards.new("done with API")
board_id = 'A5AyzrCP'
def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        print(column['name'], end='')
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(' | Всего задач: ', len(task_data))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])

def create(what='column', name='New', column_name=''):
    # Получим данные всех колонок на доске
    if what == 'column':
        response = requests.post(base_url.format(f'boards/{board_id}/lists'), data={'name': name, **auth_params})
        resulter(response.status_code)
    else:
        allColumns = {}
        column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
        # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
        for column in column_data:
            if column['name'] == column_name:
                allColumns[column['id']] = column['pos']
        if allColumns:
            if len(allColumns) == 1:
                response = requests.post(base_url.format('cards'), data={'name': name, 'idList': list(allColumns.keys())[0], **auth_params})
                resulter(response.status_code)
            else:
                print('Колонок с данным именем найдено более одной. Параметр pos показывает их позицию относительно левого края. Введите pos желаемой колонки: ')
                for val in allColumns.values():
                    print(column_name, '| pos: ', val)
                try:
                    colInp=int(input())
                except ValueError:
                        print('Такой колонки не существует, перемещение не удалось')
                else:
                    colId = None
                    for key, val in allColumns.items():
                        if val == colInp:
                            colId = key
                            break
                    if colId:
                        # Создадим задачу с именем _name_ в найденной колонке
                        response = requests.post(base_url.format('cards'), data={'name': name, 'idList': colId, **auth_params})
                        resulter(response.status_code)
                    else:
                        print(f'Не найдено колонки {column_name}')

def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Среди всех колонок нужно найти задачу по имени и получить её id
    finds = {}
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        neededCol = False
        if column['name'] == column_name:
            neededCol = True
        finds[(neededCol, column['id'], column['name'], column['pos'])] = []
        for task in column_tasks:
            if task['name'] == name:
                finds[(neededCol, column['id'], column['name'], column['pos'])].append(task['id'])
    findsCol = {key:val for key,val in finds.items() if key[0]==True}
    findsTask = {key:val for key,val in finds.items() if len(val)>0}
    lenfinds, lenfindsCol, lenfindsTask, lenfindsTaskValues = len(finds), len(findsCol), len(findsTask), len(list(findsTask.values())[0])
    if lenfindsCol == 0:
        print('Не найдена колонка')
    elif lenfindsTask == 0:
        print('Не найдена задача')
    elif lenfindsCol * lenfindsTask * lenfindsTaskValues == 1:
        response = requests.put(base_url.format('cards') + '/' + list(findsTask.values())[0][0] + '/idList', data={'value': list(findsCol.keys())[0][1], **auth_params})
        resulter(response.status_code)
    elif lenfindsCol > 0:
        if lenfindsCol == 1:
            colId = list(findsCol.keys())[0][1]
        else:
            print('Колонок с данным именем найдено более одной. Параметр pos показывает их позицию относительно левого края. Введите pos желаемой колонки: ')
            for key in findsCol.keys():
                print(key[2], '| pos: ', key[3])
            try:
                colInp=int(input())
            except ValueError:
                    print('Такой задачи не существует, перемещение не удалось')
            else:
                colId = None
                for key in findsCol.keys():
                    if key[3] == colInp:
                        colId = key[1]
        if colId:
            if lenfindsTask * lenfindsTaskValues == 1:
                response = requests.put(base_url.format('cards') + '/' + list(findsTask.values())[0][0] + '/idList', data={'value': colId, **auth_params})
                resulter(response.status_code)
            else:
                print('Задач с данным именем найдено более одной. Введите порядковый номер желаемой к перемещению задачи: ')
                num = 1
                for key, val in findsTask.items():
                    print(key[2])
                    for elem in val:
                        print('\t', num, ' | ', name)
                        num += 1
                try:
                    taskInp=int(input())
                except ValueError:
                    print('Такой задачи не существует, перемещение не удалось')
                else:
                    taskId = None
                    num = 1
                    for key, val in findsTask.items():
                        if taskId: break
                        for elem in val:
                            if num == taskInp:
                                taskId = elem
                                break
                            num += 1
                    if taskId:
                        response = requests.put(base_url.format('cards') + '/' + taskId + '/idList', data={'value': colId,**auth_params})
                        resulter(response.status_code)
                    else:
                        print('Такой задачи не существует, перемещение не удалось')
        else:
            print('Введенный pos не существует, перемещение не удалось.')

def resulter(status):
    if status == 200:
        print('Успех')
    else: print('Что-то пошло не так, статус ответа сервера - ', status)

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])

