## Проект: Foodgram - Продуктовый помощник

## Описание
Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

***
### Подготовка и запуск проекта в Docker
Установить Docker Desktop на локальный ПК

***
Клонировать репозиторий:

```
git clone https://github.com/Innis8/yamdb_final.git

```

***
Файл переменных окружения infra/.env_example нужно переименовать в .env и поместить туда необходимую информацию:
- секретный ключ Django SECTRET_KEY, использующийся для хеширования и криптографических подписей. Сгенерировать свой ключ можно, например, на сайте https://djecrety.ir/ либо выполнив в терминале команду:
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
- информацию относительно PostgreSQL DB

- список разрешенных хостов в виде host_1,host_2,host_n (через запятую, без пробелов)

***
Пример заполнения infra/.env

```
SECRET_KEY=YOUR_SECRET_KEY_FOR_SETTINGS.PY
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<<<пароль для БД>>>
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,host_1,host_2,host_N(через запятую без пробелов)(добавить также названия создаваемых докером контейнеров. Как минимум, контейнера web, создаваемого на базе папки api_yamdb)
DEBUG=DEBUG = False
```

***
Перейти в директорию infra и выполнить команду:

```
cd infra_sp2/infra
docker-compose up -d --build
```

***
Выполнить по очереди команды для создания миграций, создания суперюзера и сбора статики:

```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

***
```
Проект будет доступен по адресу: http://localhost/
Админка по адресу: http://localhost/admin/
Общая документация по адресу: http://localhost/api/docs/
```

***
Необходимо залогинится в админку под суперпользователем, созданным ранее, и добавить там в раздел `Теги` необходимое количество тегов для рецепта в формате:

`Название`

`Произвольный цвет в hex вида #FFFFFF`

`Уникальный слаг для ссылки`

Теги могут разными. Например, `Завтрак`, `Обед`, `Ужин`, `Разгрузка`, `Лёгкое`, `Сладкое`. Одному рецепту можно назначить несколько тегов, но как минимум один.

***
В админке же можно добавить список ингредиентов. При создании рецепта пользователь выбирает ингредиенты из предоставляемого сервисом списка. Можно импортировать довольно большой предварительно подготовленный список из ~2800 наименований, выполнив команду:

```
docker-compose exec backend python manage.py load_ingredients
```

***
При создании рецепта в сервисе вводить в соответствующее поле название ингредиента, и, если он присутствует в списке,  он отобразится.

***
### Остановка Docker

Для остановки контейнеров без их удаления выполнить команду:

```
docker-compose stop
```

Для остановки с удалением контейнеров и внутренних сетей, связанных с этими сервисами:

```
docker-compose down
```

Для остановки с удалением контейнеров, внутренних сетей, связанных с этими сервисами, и томов:

```
docker-compose down -v
```

***
### Запуск проекта Docker, после его остановки

Для запуска ранее остановленного проекта, если контейнеры не были удалены:

```
docker-compose start -d
```

Для запуска ранее остановленного проекта, если контейнеры были удалены, но тома - нет:

```
docker-compose up -d
```