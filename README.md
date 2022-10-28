# hw05_final
### YaTube - социальная сеть

```
Yatube - Веб приложение. Это социальная сеть для блогеров. В которой реализована
авторизация на Django, работа с Базами Данных, создание индивидуальных страниц
пользователей. Создание постов, их оценка и возможность добавить комментарии.
```

### Технологии:
- Python 3.9
- Django framework 2.2.16
- HTML
- CSS (Bootstrap 3)
- Djangorestframework-simplejwt 4.7.2
- Pillow 8.3.1
- sorl-thumbnail 12.7.0


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/p1rt-py/hw05_final.git
```

```
cd YaTube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
