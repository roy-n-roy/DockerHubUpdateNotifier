FROM python:3.8

ENV SMTP_HOST smtp.gmail.com
ENV SMPT_PORT 465

WORKDIR /data
WORKDIR /app

COPY *.py requirements.txt /app/

RUN curl -L https://github.com/pudo/dataset/archive/1.2.0.tar.gz -o dataset-1.2.0.tar.gz && tar xf dataset-1.2.0.tar.gz && pip install -r requirements.txt ./dataset-1.2.0

CMD [ "python3", "./entry_point.py" ]