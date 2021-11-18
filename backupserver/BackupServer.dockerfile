FROM ubuntu:latest
RUN apt-get update
RUN apt upgrade
RUN apt-get install nodejs net-tools -y
WORKDIR /home/sftp_manager
COPY backup_key /etc/ssh
COPY backup_key.pub /etc/ssh
COPY caserver_key.pub /etc/ssh

