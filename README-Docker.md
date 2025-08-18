# 🐳 Docker Setup для Resto Reserve

Этот документ описывает настройку и использование Docker для проекта системы бронирования ресторана.

## 📋 Требования

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd resto-reserve

# Скопируйте .env.example в .env и настройте переменные
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env`:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# База данных
DB_NAME=resto_reserve
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 3. Запуск приложения

```bash
# Собрать и запустить все сервисы
make build
make up

# Или использовать docker-compose напрямую
docker-compose up -d
```

### 4. Инициализация данных

```bash
# Создать суперпользователя
make createsuperuser

# Загрузить начальные данные
make loaddata
```

## 🛠️ Управление контейнерами

### Основные команды

```bash
# Показать справку
make help

# Запустить сервисы
make up

# Остановить сервисы
make down

# Показать логи
make logs

# Войти в контейнер Django
make shell

# Применить миграции
make migrate

# Создать миграции
make makemigrations

# Собрать статические файлы
make collectstatic

# Запустить тесты
make test
```

### Режимы работы

```bash
# Режим разработки
make dev

# Режим продакшена
make prod

# Показать статус сервисов
make status

# Перезапустить сервисы
make restart
```

## 🏗️ Архитектура

### Сервисы

1. **web** - Django приложение (порт 8000)
2. **db** - PostgreSQL база данных (порт 5432)
3. **nginx** - Nginx прокси (порт 80)

### Сети

- `resto_reserve_network` - внутренняя сеть для контейнеров

### Тома

- `postgres_data` - данные PostgreSQL
- `./static` - статические файлы Django
- `./media` - загруженные файлы

## 🔧 Конфигурация

### Nginx

Конфигурация находится в `nginx.conf`:
- Проксирование к Django
- Обслуживание статических файлов
- Gzip сжатие
- Настройки безопасности

### Django

Настройки в `config/settings.py`:
- Поддержка переменных окружения
- Настройки для Docker
- Конфигурация базы данных

## 📊 Мониторинг

### Логи

```bash
# Все сервисы
make logs

# Конкретный сервис
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### Health Check

```bash
# Проверить статус приложения
curl http://localhost/health/
```

## 🚨 Устранение неполадок

### Проблемы с базой данных

```bash
# Проверить подключение к БД
make shell
python manage.py dbshell

# Сбросить базу данных
docker-compose down -v
docker-compose up -d
```

### Проблемы с миграциями

```bash
# Принудительно применить миграции
make shell
python manage.py migrate --fake-initial
```

### Очистка

```bash
# Полная очистка
make clean

# Очистить только контейнеры
docker-compose down
```

## 🔒 Безопасность

### Продакшен настройки

1. Измените `DEBUG=False` в `.env`
2. Установите сильный `SECRET_KEY`
3. Настройте `ALLOWED_HOSTS`
4. Используйте HTTPS (настройте SSL сертификаты)

### Переменные окружения

Никогда не коммитьте `.env` файл в Git. Все секретные данные должны быть в переменных окружения.

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Запустить несколько экземпляров Django
docker-compose up -d --scale web=3
```

### Настройка балансировщика

Для продакшена рекомендуется использовать внешний балансировщик нагрузки (например, AWS ALB, GCP Load Balancer).

## 🎯 Дополнительные возможности

### Backup базы данных

```bash
# Создать backup
docker-compose exec db pg_dump -U postgres resto_reserve > backup.sql

# Восстановить backup
docker-compose exec -T db psql -U postgres resto_reserve < backup.sql
```

### Обновление приложения

```bash
# Остановить сервисы
make down

# Получить обновления
git pull

# Пересобрать и запустить
make build
make up
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте статус сервисов: `make status`
4. Обратитесь к документации Django и Docker
