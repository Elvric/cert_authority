FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y net-tools
RUN mkdir /tmp/setup
COPY ../openssl.cnf /etc/ssl
COPY setup_caserver.sh /tmp/setup/setup.sh
RUN chmod u+x /tmp/setup/setup.sh
RUN ./tmp/setup/setup.sh