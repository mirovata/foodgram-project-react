# Foodgram
## Бейджик об удачно завершенном workflow

[![Main Foodgram workflow](https://github.com/mirovata/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/mirovata/foodgram-project-react/actions/workflows/main.yml)

## Описание
Проект позволяет создавать зарегистрированным пользователям создавать свои рецепты,добавлять рецепты в избранное,подписаться на автора рецепта,скачать список покупок с нужными ингредиентами.Анонимные пользователи могут просматривать главную страницу и рецепты автора.

[![2024-02-27-083251.png](https://i.postimg.cc/L6GL1Sbr/2024-02-27-083251.png)](https://postimg.cc/ZCFCGGZc)

## Технологии
- Docker
- Django
- Djoser
- Python
- PostgreSQL
- Gunicorn
- Javascript

## Как развернуть проект

Клонируйте репозиторий:

```
git@github.com:mirovata/foodgram-project-react.git
```
В главное директории проекта создайте .env с данными:

```
DEBUG='False или True'
SECRET_KEY=Ваш секретный ключ django.
POSTGRES_DB=Имя базы.
POSTGRES_USER=Пользователь базы.
POSTGRES_PASSWORD=Пароль базы.
DB_NAME=Имя базы.
DB_HOST=Хост базы.
DB_PORT=Порт базы.
ALLOWED_HOSTS=Ваши разрешенные хосты сервера.
```

Перейдите в папку infra:

```
cd infra/
```

Запустите проект:

```
docker build up -d
```

Соберите статику:

```
docker compose exec backend python manage.py collectstatic --no-input
```

Выполните миграцию и заполните базу Тэгами и Игредиентами.

```
docker compose exec backend python manage.py migrate
```
```
docker compose exec backend python manage.py csv_import
```

## Примеры запросов и ответов

`POST` Запрос на адрес ```http://127.0.0.1:8000/api/recipes/```

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}

`GET` запрос на адрес ```http://127.0.0.1:8000/api/recipes/``` возращает:

{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}

## Автор

**Роман Ткаченко** - back-end developer 