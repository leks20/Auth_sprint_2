
FROM python:3.10

ENV PYTHONUNBUFFERED 1
WORKDIR /code

COPY ../requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY /async_api/src /code/

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind",  "0.0.0.0:8000"]