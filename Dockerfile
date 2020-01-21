FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY django/ /app/

RUN pip install -r requirements.txt

EXPOSE 3031
CMD [ "bash", "-c", "[ ! -f secret ] && echo 'SECRET_KEY="'$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~\|' | fold -w 50 | head -n 1)'"' > secret; source secret && python manage.py migrate && uwsgi uwsgi.ini" ]
 