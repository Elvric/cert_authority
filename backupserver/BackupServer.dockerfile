FROM ubuntu:latest
RUN apt-get update
RUN apt-get install nodejs net-tools -y
COPY ../openssl.cnf /etc/ssl