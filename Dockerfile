FROM python:3.13-alpine

WORKDIR /code

# Установка системных зависимостей
RUN apk add --no-cache gcc musl-dev libffi-dev libpq

# Настройка pip для использования зеркала
RUN pip install --upgrade pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Команда для запуска
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]