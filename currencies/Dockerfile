FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate
COPY . /app/