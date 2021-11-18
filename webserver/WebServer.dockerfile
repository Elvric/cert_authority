FROM ubuntu:latest
RUN apt-get update
RUN apt-get install nodejs net-tools -y
RUN mkdir /tmp/setup
COPY setup_webserver.sh /tmp/setup/setup.sh
COPY nginx /tmp/setup/nginx
COPY cert /tmp/setup/cert
RUN chmod u+x /tmp/setup/setup.sh
RUN ./tmp/setup/setup.sh
RUN apt-get install npm -y
CMD service nginx restart && npm start --prefix /webserver/frontend