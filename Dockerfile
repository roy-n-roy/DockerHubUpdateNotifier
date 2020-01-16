FROM python:3.8

ENV SMTP_HOST smtp.gmail.com
ENV SMPT_PORT 465

WORKDIR /app

COPY *.py requirements.txt /app/
RUN "mkdir /data && chmod +x *.py"

RUN pip install -r requirements.txt

CMD [ "python3", "./entry_point.py" ]