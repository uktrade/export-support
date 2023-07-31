FROM python:3.9

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN mkdir -p /app
WORKDIR /app
ADD . /app/

RUN pip install -r requirements-dev.txt

CMD /app/compose/django/start.sh
