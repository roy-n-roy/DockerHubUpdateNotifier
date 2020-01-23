FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY django/ /app/

EXPOSE 3031
RUN echo 'export SECRET_KEY="'$(cat /dev/urandom | tr -dc 'a-zA-Z0-9%&@+\-*/=^~|' | fold -w 50 | head -n 1)'"' >> ~/.bashrc
CMD [ "bash", "-c", ". ~/.bashrc && python manage.py migrate && uwsgi uwsgi.ini" ]
