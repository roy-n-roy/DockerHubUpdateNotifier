FROM python:3.8

RUN pip install requests python-dateutil schedule dataset

WORKDIR /db
WORKDIR /app

COPY entry_point.py .
RUN chmod +x entry_point.py

ENV PATH $PATH:.
ENV SMTP_HOST smtp.gmail.com
ENV SMPT_PORT 465

ENTRYPOINT [ "python3", "/app/entry_point.py" ]