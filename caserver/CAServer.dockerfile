FROM ubuntu:latest
RUN apt-get update
RUN apt-get install nodejs net-tools -y
RUN mkdir /tmp/setup
COPY setup_caserver.sh /tmp/setup/setup.sh
COPY nginx /tmp/setup/nginx
COPY cert /tmp/setup/cert
COPY openssl.cnf /etc/ssl/openssl.cnf
RUN chmod u+x /tmp/setup/setup.sh
RUN ./tmp/setup/setup.sh
CMD service nginx restart || cat /var/log/nginx/error.log && cat
