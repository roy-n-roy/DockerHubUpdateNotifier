FROM python:3.8

RUN pip install requests dataset python-dateutil schedule tabulate

WORKDIR /db
WORKDIR /app

COPY *.py /app/
RUN chmod +x *.py

ENV PATH $PATH:.
ENV SMTP_HOST smtp.gmail.com
ENV SMPT_PORT 465

CMD [ "entry_point.py" ]