FROM mysql:5.7.36
ENV MYSQL_ROOT_PASSWORD=FiE5HF4xHOsPIL9n
COPY setup_database.sh /docker-entrypoint-initdb.d/setup.sh
RUN apt-get update
RUN apt install -y net-tools
RUN mkdir /tmp/setup
COPY imovies_users.sql /tmp/setup/imovies_users.sql
COPY initdatabase.sql /tmp/setup/initdatabase.sql
COPY my.cnf /etc/mysql/my.cnf
COPY ./cert/cacert.pem /etc/ssl/cacert.pem
COPY ./cert/db.pem /etc/ssl/certs/db.pem
COPY ./cert/db-key-pkcs1.pem /etc/ssl/private/db-key-pkcs1.pem
RUN chown mysql /etc/ssl/*pem
RUN chown mysql /etc/ssl/private/db-key-pkcs1.pem
RUN chmod 777 /etc/ssl/private/db-key-pkcs1.pem