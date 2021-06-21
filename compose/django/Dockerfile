FROM python:3.9

RUN mkdir -p /app
WORKDIR /app
ADD . /app/

RUN pip install -r requirements-dev.txt
RUN pip install -r requirements.txt

CMD /app/compose/django/start.sh
