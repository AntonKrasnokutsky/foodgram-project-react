# API_YAmdb

## Авторы
Разработка курса и заданий Яндекс.Практикум
Иполнитель: Антон Краснокутский

## Описание
Проект разрабатывался на курсе Python-разработчик Яндекс.Практикум. Является учебным димпломным проектом по изучению Django REST framework.
Предоставляет следующие эндпоинты:
- Авторизация (/api/users/)
- Тэги (/api/tags/)
- Ингридиенты (/api/ingredients/)
- Рецепты (/api/recipes/)
- Подписки (/api/users/subscriptions/)
- Изранное (/api/recipes/{id}/favorite/)
- Управлеие пользователями (/api/v1/users/)
- Изменение списка покупок (/api/recipes/{id}/shopping_cart/)
- Скачать список покупок (/api/recipes/download_shopping_cart/)

## Технология
API_yatube использует ряд технологий:

- Django 4.2
- Django REST framework 3.14
- Djoser 2.2
- Django filter 23.2

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AntonKrasnokutsky/foodgram-project-react.git
```

```
cd foodgram-project-react/backend/
```

Создать файл с переменными окружения

```
nano .env
```
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Пример запроса
При использовании на локальном сервере
#### Получение произведения
```
method GET
http://localhost/api/recipes/
```
Пример ответа
```
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
```

#### Подробная информация о запросах здесь:
```
http://localhost/api/docs/
```
