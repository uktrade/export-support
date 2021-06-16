FROM node:14

RUN mkdir -p /app
WORKDIR /app
ADD . /app/

RUN npm set unsafe-perm true
RUN npm install

CMD /app/compose/webpack/start.sh
