FROM ubuntu:latest
RUN apt-get update
RUN apt-get install net-tools -y
RUN mkdir /tmp/setup
ENV PATH="/caserver/api/venv/bin:${PATH}"
COPY setup_caserver.sh /tmp/setup/setup.sh
COPY nginx /tmp/setup/nginx
COPY cert /tmp/setup/cert
COPY intermediate /etc/ssl/intermediate/
RUN chmod u+x /tmp/setup/setup.sh
RUN ./tmp/setup/setup.sh
CMD service nginx restart && uwsgi --ini /caserver/api/uwsgi.ini

