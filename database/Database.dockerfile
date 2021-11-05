FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=FiE5HF4xHOsPIL9n
COPY setup_database.sh /docker-entrypoint-initdb.d/setup.sh
RUN apt-get update
RUN apt install -y net-tools
RUN mkdir /tmp/setup
COPY ../openssl.cnf /etc/ssl
COPY imovies_users.sql /tmp/setup/imovies_users.sql
COPY initdatabase.sql /tmp/setup/initdatabase.sql