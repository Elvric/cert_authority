FROM ubuntu:latest
RUN apt-get update
RUN apt install -y net-tools iptables
RUN mkdir /tmp/setup
COPY setup_firewall.sh /tmp/setup/setup.sh
COPY ../openssl.cnf /etc/ssl
RUN chmod u+x /tmp/setup/setup.sh
CMD ./tmp/setup/setup.sh && tail -f /dev/null
