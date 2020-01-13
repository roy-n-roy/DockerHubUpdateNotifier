FROM python:3.8

RUN pip install requests python-dateutil schedule

WORKDIR /db
WORKDIR /app

COPY entry-point.py .
RUN chmod +x entry-point.py

ENV PATH $PATH:.
ENV SMTP_HOST smtp.gmail.com
ENV SMPT_PORT 465

ENTRYPOINT [ "/app/entry-point.py" ]