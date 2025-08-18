# 🔧 Настройка сервера для деплоя

## 📋 Информация о сервере
- **IP адрес**: 130.193.34.169
- **Название**: test2
- **Пользователь для деплоя**: deploy

## 🚀 Пошаговая настройка

### 1. Подключение к серверу
```bash
ssh root@130.193.34.169
```

### 2. Создание пользователя deploy
```bash
# Создать пользователя
sudo useradd -m -s /bin/bash deploy

# Добавить в группу sudo
sudo usermod -aG sudo deploy

# Установить пароль (временно)
echo "deploy:deploy123" | sudo chpasswd
```

### 3. Настройка SSH для пользователя deploy
```bash
# Создать папку .ssh
sudo mkdir -p /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Создать файл authorized_keys
sudo touch /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

### 4. Добавить публичный ключ
```bash
# Открыть файл для редактирования
sudo nano /home/deploy/.ssh/authorized_keys
```

**Вставить следующий публичный ключ:**
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDC8A2GtvDkW1VHDd97NSAjtlz5ckgwLUCdXE8KQqtJCjQ9xinEZmB9L2LnaXafMKaIiysygUBiQIHYTQc7Y5HcSr1P+hm2vUhtIy5nHGqmqhjihC4Q5IlIXojZcAnYBQZ6A21VP9zfFNh1164ioLp/ZE4uB0BDPHx//nI3d7C0580pnwJrrSAIPxAwLZTyv8l6DmA/s+sbeuYat/a5tjfwGmU6NHUo+6epD5ppZZnK2zCT5RjEHQcRhUdq/CFT4Hos0hLGV8Qzw9vJoX7ZB+YGowZCiWZaysXT03u+TQHPFsbJ4OeFRVDg2kHeJ8Q/sJKU+vA/OstXLsEsOgU6pkAlgdeidituygfFuu3wVEhqTyG8MI5pz+KCIxIDQjSCxLHX384xVvRAbPJ/6q0BiE/70ZC6dofIJ7Bvaae1FfARS1tRbgxrwLfu6ADfukRXZECj0hFIxBA2mFs4KpJx+SXHhqYLxuAm+Ead5gVetNkm0Rheg07yFI3894MRSluHAu/nWAFMDjdvH4GNEzHg/pp3Z1lY7YiefxUHvnZu/Hy93EbG+Qway+urtEP+WBZz6MaDfnOkNvzjkN0nh1VQUYlEhjTuBK4i8ihvUCigq4Sga1YFqJq4/O4mxnLNr0qxPSK8mHRGVDrHeZgn3QhviUlHd79R8gfW804sUP7e1SYTNw== kcenka@DESKTOP-GUFNDUR
```

### 5. Установка Docker
```bash
# Обновить систему
sudo apt-get update -y
sudo apt-get upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавить пользователя deploy в группу docker
sudo usermod -aG docker deploy

# Удалить скрипт установки
rm get-docker.sh
```

### 6. Установка Docker Compose
```bash
# Скачать Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Сделать исполняемым
sudo chmod +x /usr/local/bin/docker-compose

# Проверить установку
docker-compose --version
```

### 7. Создание папки проекта
```bash
# Создать папку для проекта
sudo mkdir -p /home/deploy/resto-reserve
sudo chown deploy:deploy /home/deploy/resto-reserve
```

### 8. Тестирование подключения
```bash
# Переключиться на пользователя deploy
sudo su - deploy

# Проверить, что SSH работает
ssh deploy@localhost

# Выйти из пользователя deploy
exit
```

### 9. Настройка брандмауэра
```bash
# Включить UFW
sudo ufw --force enable

# Настроить правила
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Проверить статус
sudo ufw status
```

## 🔑 Проверка настройки

### Тест SSH подключения с вашего компьютера:
```bash
ssh deploy@130.193.34.169
```

Если подключение успешно, вы должны увидеть приглашение командной строки.

### Тест Docker:
```bash
# Подключиться к серверу
ssh deploy@130.193.34.169

# Проверить Docker
docker --version
docker-compose --version
```

## 📝 Секреты для GitHub Actions

После успешной настройки сервера добавьте следующие секреты в GitHub:

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Имя секрета | Значение |
|-------------|----------|
| `DEPLOY_HOST` | `130.193.34.169` |
| `DEPLOY_USER` | `deploy` |
| `SSH_PORT` | `22` |
| `DEPLOY_KEY` | [Приватный ключ из файла] |
| `DEBUG` | `False` |
| `SECRET_KEY` | [Ваш Django SECRET_KEY] |
| `DB_PASSWORD` | `261110170712` |
| `TELEGRAM_BOT_TOKEN` | `7225452454:AAGHINaP92ikXDF3HMAQh7gUUiMp8tzi4N0` |
| `TELEGRAM_CHAT_ID` | `1845323660` |

## 🚨 Устранение неполадок

### Если SSH не подключается:
1. Проверьте, что публичный ключ добавлен правильно
2. Проверьте права доступа к файлам:
   ```bash
   ls -la /home/deploy/.ssh/
   ```
3. Проверьте логи SSH:
   ```bash
   sudo tail -f /var/log/auth.log
   ```

### Если Docker не работает:
1. Проверьте, что Docker установлен:
   ```bash
   docker --version
   ```
2. Проверьте, что пользователь в группе docker:
   ```bash
   groups deploy
   ```

### Если деплой не работает:
1. Проверьте секреты в GitHub
2. Проверьте логи GitHub Actions
3. Проверьте подключение к серверу вручную

## ✅ Готово!

После выполнения всех шагов ваш сервер будет готов к автоматическому деплою через GitHub Actions.
