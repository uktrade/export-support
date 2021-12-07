FROM python:3.9

RUN mkdir -p /app
WORKDIR /app

ADD ./requirements-dev.txt /app/requirements-dev.txt
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install -r requirements.txt

ADD . /app/

CMD /app/compose/django/start.sh
