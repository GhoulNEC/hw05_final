# yatube_project
### Описание
Социальная сеть Yatube. Реализована система авторизации. 
Через сервис у авторизированного пользователя открываются возможности: публикации новых постов, подписки на авторов с отображением их постов во вкладке "Подписки",
комментирование постов, редактирования профиля. Реализована система подкомментариев с использованием библиотеки ```mptt```.
### Технологии

* Python 3.8
* Django 2.2.19

### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- В папке с файлом manage.py выполните команду
```
python3 manage.py runserver
```
### Автор
Роман