FROM python:3.12-bullseye
WORKDIR /app
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["uwsgi", "app.ini"]