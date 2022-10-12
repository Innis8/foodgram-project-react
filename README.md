## Проект: Foodgram - Продуктовый помощник

![Status of workflow runs triggered by the push event](https://github.com/innis8/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

Проект доступен по адресу: `http://178.154.226.19/`

Админка по адресу: `http://178.154.226.19/admin/`

Общая документация по адресу: `http://178.154.226.19/api/docs/`

Пользователи сайта:

```
admin@admin.com:qwe
finwe@winwe.com:qazxsw21
orome@orome.com:qazxsw21
```

## Описание
Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.



***
## Workflow
Запускается при пуше в ветку `master`, не запускается, если в коммите была лишь правка файла `README.md`

Состоит из следующих шагов:

`tests`: установка зависимостей, запуск тестов flake8 и pytest

`build_and_push_foodgram_backend_to_docker_hub`: сборка образа foodgram_backend и отправка в свой репозиторий на DockerHub

`build_and_push_foodgram_frontend_to_docker_hub`: сборка образа foodgram_frontend и отправка в свой репозиторий на DockerHub

`deploy`: разворачивание проекта на удалённом сервере

`send_message`: отправка уведомления в телеграм-чат при успешном прохождении workflow в GitHub Actions

***
### Подготовка и запуск проекта в Docker

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

- разместить настроенный файл infra/.env на удаленный сервер в home/<ваш_username>/.env

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
ALLOWED_HOSTS=localhost,127.0.0.1,host_1,host_2,host_N(Через запятую без пробелов. Добавить также названия создаваемых докером контейнеров. Например, контейнеров backend, frontend, db, nginx)
DEBUG=False (на проде)
```

***
### Установка на удаленном сервере (Ubuntu):
1\. Войти на свой удалённый сервер:

```
ssh <your_login>@<ip_address>
```

2\. Установить Docker на удалённый сервер:

```
sudo apt install docker.io
```

3\. Установить docker-compose на удалённый сервер:
 - Проверить, какая последняя версия доступна на [странице релизов](https://github.com/docker/compose/releases 'https://github.com/docker/compose/releases'). На момент написания настоящего документа наиболее актуальной стабильной версией является v2.11.2
 - Следующая команда загружает версию 2.11.2 и сохраняет исполняемый файл в каталоге `/usr/local/bin/docker-compose`, в результате чего данное программное обеспечение будет глобально доступно под именем `docker-compose`:

```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.11.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

- Затем необходимо задать правильные разрешения, чтобы сделать команду docker-compose исполняемой:

```
sudo chmod +x /usr/local/bin/docker-compose
```

- Чтобы проверить успешность установки, запустить следующую команду:

```
docker-compose --version
```

- Вывод будет выглядеть следующим образом:

```
Docker Compose version v2.11.2
```

4\. Скопировать файлы `infra/.env`, `infra/docker-compose.yaml` и `infra/nginx.conf` из проекта на удаленный сервер в `home/<ваш_username>/.env`, `home/<ваш_username>/docker-compose.yaml` и `home/<ваш_username>/nginx.conf` соответственно. Сделать это можно при помощи сторонней программы, например, WinSCP, либо выполнив следующую команду из корневой папки проекта:

```
scp infra/.env <username>@<host>:/home/<username>/infra/.env
scp infra/docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp -r infra/nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

5\. Добавить переменные окружения в Secrets на GitHub:

```
DOCKER_USERNAME=<<<<<<имя пользователя DockerHub>>>
DOCKER_PASSWORD=<<<пароль DockerHub>>>
REMOTE_USER=<<<имя пользователя удалённого сервера>>>
REMOTE_HOST=<<<IP-адрес удалённого сервера>>>
TELEGRAM_TO=<<<ID своего телеграм-аккаунта>>>
TELEGRAM_TOKEN=<<<токен своего бота>>>
SSH_KEY=<<<приватный SSH-ключ, получить можно выполнив команду на локальной машине: cat ~/.ssh/id_rsa>>>
```

- Следующие Secrets стоит добавлять, если в предыдущем шаге не заполнялся и не отправлялся на сервер файл infra/.env. В таком случае он заполнится ими и отправится на сервер автоматически в процессе workflow:

```
SECRET_KEY: свой секретный ключ из settings.py, который генерируется в процессе создания приложения, либо сгенерировать самостоятельно по инструкции выше. Сам ключ при добавлении в SECRETS обернуть в двойные кавычки "". Связано это с тем, что в процессе workflow эти данные будут будут выгружаться в файл переменных окружения .env при помощи bash и команды `echo`. Но, так как в SECRET_KEY часто встречаются символы, рацсениваемые, как спецсимволы, например ) или (, то передача строки в файл может оборваться. Для этого и нужно обернуть строку в "". Сами кавычки не передадутся в файл и не изменят итоговый SECRET_KEY

DB_ENGINE: django.db.backends.postgresql
DB_NAME: postgres
POSTGRES_USER: postgres
POSTGRES_PASSWORD: <<<пароль для БД>>>
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=host_1,host_2,host_N(через запятую без пробелов)(Через запятую без пробелов. Добавить также названия создаваемых докером контейнеров. Например, контейнеров backend, frontend, db, nginx)
```

***
### После деплоя

Зайти на удалённый сервер и выполнить по очереди команды для создания миграций, создания суперюзера и сбора статики:

```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

***
```
Проект будет доступен по адресу: `http://<IP-адрес удаленного сервера>/`

Админка по адресу: `http://<IP-адрес удаленного сервера>/admin/`

Общая документация по адресу: `http://<IP-адрес удаленного сервера>/api/docs/`

Если зарегистрировано доменное имя, можно использовать его вместо IP-адреса удаленного сервера>. То же самое насчёт протокола https.
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
sudo docker-compose exec backend python manage.py load_ingredients
```

***
При создании рецепта в сервисе вводить в соответствующее поле название ингредиента, и, если он присутствует в списке,  он отобразится. названия ингредиентов чувствительны к регистру.

***
### Остановка Docker
Если команда не выполняется и в терминале говорится о недостатке прав, вставить перед командой `sudo`

Для остановки контейнеров без их удаления выполнить команду:

```
sudo docker-compose stop
```

Для остановки с удалением контейнеров и внутренних сетей, связанных с этими сервисами:

```
sudo docker-compose down
```

Для остановки с удалением контейнеров, внутренних сетей, связанных с этими сервисами, и томов:

```
sudo docker-compose down -v
```

***
### Запуск проекта Docker, после его остановки

Для запуска ранее остановленного проекта, если контейнеры не были удалены:

```
sudo docker-compose start -d
```

Для запуска ранее остановленного проекта, если контейнеры были удалены, но тома - нет:

```
sudo docker-compose up -d
```


***
***
***
### Запуск проекта в Docker на локальном ПК

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
ALLOWED_HOSTS=localhost,127.0.0.1,host_1,host_2,host_N(через запятую без пробелов)(Через запятую без пробелов. Добавить также названия создаваемых докером контейнеров. Например, контейнеров backend, frontend, db, nginx)
DEBUG=TRUE (для тестовых запусков, на проде заменить на FALSE)

***
Перейти в директорию infra и выполнить команду:

```
cd infra_sp2/infra
docker-compose up -d
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
