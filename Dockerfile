# Версия Python
FROM python:3.11-slim-buster

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем зависимости и устанавливаем их
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . .

# Открываем порт, на котором слушает FastAPI
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]