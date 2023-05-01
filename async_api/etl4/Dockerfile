# Делаем образ для работы с ETL
FROM python:3.10-slim

RUN apt update -y && apt install libpq-dev python-dev -y && apt install build-essential -y

WORKDIR /opt/app


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./main.py"]



