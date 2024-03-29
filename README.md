# Агрегатор рецептов Recipe Keeper v1.0

## Веб приложение, с помощью которого пользователи смогут найти для себя подходящие рецепты приготовления еды, добаавить эти рецепты в избранное, а также подписаться на авторов наиболее полюбившихся им рецептов. Также проект дает возможность формировать список продуктов, необходимых для приготовления любимых блюд.

##  Автор
[@renzhin](https://github.com/renzhin)

## Используемые технологии
•   React<br>
•   Python<br>
•   Django<br>
•   DRF<br>
•   PostgreSQL<br>

## Проект развернут по адресу:
https://recipe-keeper.renzhin.ru/


## Инструкция по запуску проекта на удаленном сервере с помощью Docker:

Клонируем репозиторий:
````
git@github.com:renzhin/recipe-keeper.git
````

На виртуальном сервере создаем директорию проекта с именем recipe-keeper/

Копируем в папку recipe-keeper/ файл с переменными окружения .env и файл оркестрации контейнеров docker-compose.production.yml

Запускайем docker-compose.production.yml в режиме демона командой:
````
sudo docker compose -f docker-compose.production.yml up -d 
````

Собираем статику в контейнере backend:
````
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
````

Копируем собранную статику:
````
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
````

Выполняем миграции:
````
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
````

Создаем суперпользователя:
````
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
````

Загружаем фикстуры ингредиентов:
````
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
````

Загружаем фикстуры тэгов:
````
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_tags
````

Пример заполнения файла с переменными окружения.env:
````
# Файл .env
POSTGRES_DB=django
POSTGRES_USER=recipekeeper_user
POSTGRES_PASSWORD=mysecretpassword
DB_NAME=recipekeeper_db
# Добавляем переменные для Django-проекта:
DB_HOST=db
DB_PORT=5432
# Добавляем ключ в settyngs.py
SECRET_KEY=django-insecure-1234567891011121223321231232323232321323
# Режим отладки
DEBUG_MODE=False
# Адреса хостов
ALLOW_HOSTS='188.32.4.36 127.0.0.1 localhost recipe-keeper.renzhin.ru'
# Проброс порта Nginx
WEB_PORT=9876

````

## В API проекта доступны следующие эндпоинты:

**/api/users/**<br>
Get Получение списка пользователей.<br>
POST Регистрация нового пользователя. Доступ: без токена.
***

**/api/users/{id}**<br>
GET Персональная страница пользователя с указанным id. Доступ: без токена.
***

**/api/users/me/**<br>
GET Страница текущего пользователя.<br>
PATCH Редактирование собственной страницы. Доступ: авторизованный пользователь.
***

**/api/users/set_password**<br>
POST Изменение своего пароля. Доступ: авторизованный пользователь.
***

**/api/auth/token/login/**<br>
POST Получение токена. Используется для авторизации по емейлу и паролю для дальнейшего использования токена при запросах.
***

**/api/auth/token/logout/**<br>
POST Удаление выданного ранее токена.
***

**/api/tags/**<br>
GET Получение списка всех тегов. Доступ: без токена.
***

**/api/tags/{id}**<br>
GET Получение информации о теге о его id. Доступ: без токена.
***

**/api/ingredients/**<br>
GET Получение списка всех ингредиентов. <br>Подключён поиск по частичному вхождению в начале названия ингредиента. Доступ: без токена.
***

**/api/ingredients/{id}/**<br>
GET Получение информации об ингредиенте по его id. Доступ: без токена.
***

**/api/recipes/**<br>
GET Получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора. Доступ: без токена.<br>
POST Добавление нового рецепта. Доступ: авторизованный пользователь.
***

**/api/recipes/?is_favorited=1**<br>
GET Получение списка всех рецептов, добавленных в избранное. Доступ: авторизованный пользователь.
***

**/api/recipes/is_in_shopping_cart=1**<br>
GET Получение списка всех рецептов, добавленных в список покупок. Доступ: авторизованный пользователь.
***

**/api/recipes/{id}/**<br>
GET Получение информации о рецепте по его id (доступно без токена).<br>
PATCH Изменение своего рецепта. Доступ: автор рецепта.<br>
DELETE Удаление своего рецепта. Доступ: автор рецепта.
***

**/api/recipes/{id}/favorite/**<br>
POST Добавление нового рецепта в избранное.<br>
DELETE удаление рецепта из избранного. Доступ: авторизованный пользователь.
***

**/api/recipes/{id}/shopping_cart/**<br>
POST Добавление нового рецепта в список покупок.<br>
DELETE Удаление рецепта из списка покупок. Доступ: авторизованный пользователь.
***

**/api/recipes/download_shopping_cart/**<br>
GET Получение текстового файла со списком покупок. Доступ: авторизованный пользователь.
***

**/api/users/{id}/subscribe/**<br>
GET Подписка на пользователя с указанным id.<br>
POST Отписка от пользователя с указанным id. Доступ: авторизованный пользователь.
***

**/api/users/subscriptions/**<br>
GET Получение списка всех пользователей, на которых подписан текущий пользователь. <br>Доступ: авторизованный пользователь.
***