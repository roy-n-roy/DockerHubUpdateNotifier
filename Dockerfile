FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY django/ /app/

RUN pip install -r requirements.txt

EXPOSE 3031
CMD [ "uwsgi", "./uwsgi.ini" ]