FROM python:3.8-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app

RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r /app/requirements.txt
