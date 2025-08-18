# 🚀 Быстрая настройка VM test2

## 📋 Информация
- **Название**: test2
- **IP**: 130.193.34.169
- **Пользователь**: deploy

## ⚡ Быстрый старт

### 1. Подключение к VM
```bash
ssh root@130.193.34.169
```

### 2. Установка необходимого ПО
```bash
# Обновление системы
sudo apt-get update -y
sudo apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Nginx
sudo apt-get install -y nginx
```

### 3. Создание пользователя deploy
```bash
# Создание пользователя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Создание директории проекта
sudo mkdir -p /home/deploy/resto-reserve
sudo chown -R deploy:deploy /home/deploy/resto-reserve
```

### 4. Настройка SSH
```bash
# Создание директории .ssh
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Добавление вашего публичного ключа
sudo nano /home/deploy/.ssh/authorized_keys
# Вставьте содержимое: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC++5GdzIYIlEmhz0b063zCewdhk1fIG/0bXSAZ7qFTDR6DAAPrAbGCxbzcDUy0MDwMwguAN6zswFKDmQP51D0fpGzqoZyJXmr9xgE+Rj7E1RbSznlBSbnqGFY3S4Q8F5J/dEicrcIRaMY2uTkCJNf/kp8JZzCOx+eRK+S0Dy715H7t3J1vdfjtIEYNWhMbguO1jewWE5GgIlD6A5qXLxr5929fMTXzJ8A5MxvpwZwwcLRgCAlmGnjuVmDa1AHtXG4QEhO2OLKblymz7Kv/+zBy5uXJHUflMp3Mx9ISZca+YA3L4uY3uABbQ/xeYmOCg/r3Xx5eH2b0X/gf9+JFPly1I2Ds4Y9XsAHeEyv/7xsXYZ787aPW7SfR2CntVGVg4q1dEvwjD8CYezdA4fnFP8CkpV1KlngJPAaSL1bGO7fR8Ed5I5ckpnVQC5FC8GeqqA5N9W6GQMdkZ/TsWIu0BPgSfOqv1yNWSYlJJ5rsYsvVxjkYoEGq4VD0LjY25wgwJLyFg2+oInmjfRfurST+XrGSV2V0YVBIG/2LYu7bC+RK88AVg5ftow7fZTkr47TUvvHoNOZSGmLW90OklllmoJvH3EAUYOC6/uy3utNQJHnou4p4xy1mE+4Zdtt/+bZ79QJzjUrNhG9P5ejd8ieZ/rNm1uYnQ8Ml5bd1HDiaLLMz0Q== deploy@dzukija

# Установка прав
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

### 5. Настройка брандмауэра
```bash
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 6. Настройка Nginx
```bash
# Создание конфигурации
sudo tee /etc/nginx/sites-available/dzukija > /dev/null << 'EOF'
server {
    listen 80;
    server_name 130.193.34.169;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/deploy/resto-reserve/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/deploy/resto-reserve/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
EOF

# Активация конфигурации
sudo ln -sf /etc/nginx/sites-available/dzukija /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

## 🔑 GitHub Actions секреты

Добавьте в GitHub репозиторий:

| **Name** | **Value** |
|----------|-----------|
| `DEPLOY_HOST` | `130.193.34.169` |
| `DEPLOY_USER` | `deploy` |
| `DEPLOY_KEY` | [приватный SSH ключ] |

### Получение приватного ключа:
```bash
type C:\Users\Ксюша\.ssh\dzukija_deploy
```

## 🧪 Тестирование

### Проверка подключения
```bash
ssh deploy@130.193.34.169
```

### Ручной деплой
```bash
ssh deploy@130.193.34.169
cd /home/deploy
git clone https://github.com/your-username/resto-reserve.git
cd resto-reserve
cp env.example .env
# Настройте .env файл
docker-compose up -d
```

## 🌐 Результат

После настройки приложение будет доступно по адресу:
**http://130.193.34.169**

## 📞 Поддержка

При проблемах:
1. Проверьте логи: `docker-compose logs`
2. Проверьте статус: `docker-compose ps`
3. Создайте issue в GitHub
