FROM mysql:5.7.36
ENV MYSQL_ROOT_PASSWORD=FiE5HF4xHOsPIL9n
COPY openssl.cnf /etc/ssl/openssl.cnf
ENV OPENSSL_CONF=/etc/ssl/openssl.cnf
COPY setup_database.sh /docker-entrypoint-initdb.d/setup.sh
RUN apt-get update
RUN apt install -y net-tools
RUN mkdir /tmp/setup
COPY imovies_users.sql /tmp/setup/imovies_users.sql
COPY initdatabase.sql /tmp/setup/initdatabase.sql
COPY my.cnf /etc/mysql/conf.d
COPY ./cert/cacert.pem /etc/mysql/ssl/cacert.pem
COPY ./cert/db.pem /etc/mysql/ssl/db-cert.pem
COPY ./cert/db.key /etc/mysql/ssl/db-key.pem
RUN chown mysql /etc/mysql/ssl/db-cert.pem
RUN chown mysql /etc/mysql/ssl/db-key.pem
RUN chmod 644 /etc/mysql/ssl/cacert.pem
RUN chmod 644 /etc/mysql/ssl/db-cert.pem
RUN chmod 600 /etc/mysql/ssl/db-key.pem
