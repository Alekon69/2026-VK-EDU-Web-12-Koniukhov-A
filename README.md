
# Ask Me

## Страницы сайта

- `/` — новые вопросы.
- `/hot/` — популярные вопросы.
- `/question/1/` — вопрос с ответами.
- `/tag/python/` — вопросы по тегу.
- `/ask/` — создание вопроса.
- `/login/` — вход.
- `/signup/` — регистрация.
- `/profile/` — настройки профиля.
- `/admin/` — административная панель Django.

## Запуск через Docker

Требуются Docker и Docker Compose.

1. Создать файл настроек:

```bash
cp .env.example .env.docker
```

2. Запустить контейнеры:

```bash
docker compose up -d --build
```

3. Применить миграции:

```bash
docker compose exec web python manage.py migrate
```

4. Создать суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

5. Заполнить базу тестовыми данными:

```bash
docker compose exec web python manage.py fill_db 100
```

Сайт доступен по адресу http://localhost:8000/

Административная панель:
http://localhost:8000/admin/

Остановка контейнеров:

```bash
docker compose down
```

Данные PostgreSQL сохраняются в именованном Docker volume.

## Локальный запуск через WSL

Требуются Python и PostgreSQL.

1. Создать файлы окружения:

```bash
cp .env.example .env.docker
cp .env.example .env.local
```

2. В `.env.local` заменить:

```dotenv
DB_HOST=127.0.0.1
```

Значения POSTGRES_DB, POSTGRES_USER и POSTGRES_PASSWORD
должны совпадать в обоих файлах.

3. Запустить контейнер PostgreSQL:

```bash
docker compose up -d db
```

4. Создать виртуальное окружение и установить зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

5. Применить миграции и запустить сервер:

```bash
python manage.py migrate
python manage.py runserver
```

## Генерация тестовых данных

Команда:

```bash
python manage.py fill_db 100
```

создаёт:

- 100 пользователей и профилей;
- 1 000 вопросов;
- 10 000 ответов;
- 100 тегов;
- 20 000 оценок вопросов и ответов.

Для Docker используется:

```bash
docker compose exec web python manage.py fill_db 100
```

Коэффициент `ratio` определяет количество создаваемых
записей. Повторный запуск добавляет новые данные.
