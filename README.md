# hw05_final
### YaTube - социальная сеть

```
Социальная сеть с возможностью регистрации и ведения своего блога. 
Посты могут содержать изображения и текст. Также они могут быть объединены в сообщества. 
Есть возможность подписаться на автора, прокомментировать пост, вступить в сообщество.
Есть общая лента всей сети и персональная лента подписок.
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
[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
