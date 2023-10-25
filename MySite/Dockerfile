FROM python:3.9-alpine3.16
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем рабочую директорию
WORKDIR /MySite

# Создаем директорию /temp и копируем requirements.txt в нее
RUN mkdir /temp

# Создаем и устанавливаем виртуальное окружение
#RUN python -m venv venv
#ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt /temp/requirements.txt

RUN pip install -r /temp/requirements.txt

# Копируем все файлы из директории MySite в /MySite
COPY . /MySite

# Открываем порт 8000
EXPOSE 8000

# Запускаем команду для старта приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Создаем пользователя adminsan
#RUN adduser --disabled-password adminsan

# Переключаемся на пользователя adminsan
#USER adminsan