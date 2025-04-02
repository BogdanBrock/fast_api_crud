## 💻 Технологии:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?style=flat&logo=FastAPI&logoColor=56C0C0&color=008080)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-464646?style=flat&logo=SQLAlchemy&logoColor=56C0C0&color=008080)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/-Pydantic-464646?style=flat&logo=Pydantic&logoColor=56C0C0&color=008080)](https://pydantic-docs.helpmanual.io/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&logo=JSON-web-tokens&logoColor=56C0C0&color=008080)](https://jwt.io/)

## Описание проекта fast_api_crud
"fast_api_crud" - это API, где пользователь может просматривать свой профиль, 
категории, продукты, отзывы на продукты. Пользователь может регистрироваться, 
присутствует система аутентификации по jwt токену, так же имеется ролевая модель, 
где есть: администратор, поставщик, покупатель. Администратор может совершать 
любые действия на сервере, создавать, изменять и удалять товары. Создавать 
категории может только администратор. Создавать продукты могут поставщики, 
а оставлять отзывы на эти продукты могут все авторизованные пользователи. 
Пользователь помимо категории может создавать для нее подкатегории, так же 
можно найти не только все категории, но и все подкатегории по фильтру 
для этой категории. Так же фильтрация доступна и по другим ресурсам.

## Инструкция как развернуть проект в докере

- Нужно склонировать проект из репозитория командой:
```bash
git clone git@github.com:BogdanBrock/fast_api_crud.git
```
- Для развертывания проекта, в корне проекта нужно
создать .env файл, можно скопировать данные из .env.example

- Находясь в проекте, перейти в папку под названием "docker":
```bash
cd docker
```

- Выполнить команду с включенным докером:
```bash
docker compose up
```

- После того как докер запустился, нужно создать миграции, 
важно при этом, чтобы был запущен докер с контейнерами:
```bash
docker compose exec app alembic revision --autogenerate -m 'Initial migration'
```

- После создания миграций мы создаем базу данных по команде:
```bash
docker compose exec app alembic upgrade head
```

- Все маршруты доступны по адресу:
```bash
http://127.0.0.1:8000/docs#/
```