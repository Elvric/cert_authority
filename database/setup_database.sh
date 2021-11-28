#!/bin/bash
DBPASSWD=FiE5HF4xHOsPIL9n

debconf-set-selections <<< "mysql-server mysql-server/root_password password $DBPASSWD"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $DBPASSWD"

sudo apt update
sudo apt install mysql-server net-tools -y

mysql -u root -p$DBPASSWD -e "CREATE DATABASE imovies"
mysql -u root -p$DBPASSWD imovies < imovies_users.sql
mysql -u root -p$DBPASSWD imovies < initdatabase.sql

cp my.cnf /etc/mysql/conf.d
mkdir /etc/mysql/ssl
cp ./cert/cacert.pem /etc/mysql/ssl/cacert.pem
cp ./cert/db.pem /etc/mysql/ssl/db-cert.pem
cp ./cert/db.key /etc/mysql/ssl/db-key.pem
sudo chown mysql /etc/mysql/ssl/db-cert.pem
sudo chown mysql /etc/mysql/ssl/db-key.pem
sudo chmod 644 /etc/mysql/ssl/cacert.pem
sudo chmod 644 /etc/mysql/ssl/db-cert.pem
sudo chmod 600 /etc/mysql/ssl/db-key.pem
sudo sed -i -e "s/127.0.0.1/172.27.0.3/g" /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i -r 's/^#( general_log)/\1/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql

# setup backup
mkdir ssh_keys
mv db_priv_key ssh_keys
touch mysql_backup.sh
cat << 'EOL' > mysql_backup.sh
#!/bin/bash

curr_date=`date +"%Y-%m-%d"`

mysqldump -u root --password=$DBPASSWD imovies users > imovies_users_bkp_$curr_date.sql

 rm .ssh/known-host

sftp -i ssh_keys/db_priv_key dbackup@172.27.0.4 << !
put imovies_users_bkp_$curr_date.sql
quit
!


rm imovies_users_bkp_$curr_date.sql
EOL
#TODO: dbackup's backupserver password is prompted after sftp command --> maybe because this user has a password on backupserver
crontab -l > cron_tmp
echo "* * * * * mysql_backup.sh" > cron_tmp
crontab cron_tmp
rm cron_tmp

# rsyslog
apt install rsyslog-gnutls -y
cp cert/cacert.pem /etc/ssl/certs/
cp rsyslog.conf /etc/rsyslog.conf
systemctl restart rsyslog