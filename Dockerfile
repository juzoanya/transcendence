FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD [ "python manage.py", "runserver 0.0.0.0:8080" ]
