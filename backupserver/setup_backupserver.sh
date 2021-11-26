#!/bin/bash
cat <<EOF >> /etc/ssh/sshd_config
Match Group sftp_users
  ChrootDirectory /data/%u
  ForceCommand internal-sftp -u 0227 -P remove,rmdir
EOF
mkdir -p /data
chmod 701 /data
groupadd sftp_users
users=(dbackup cabackup)
# TODO remove if loging with certs
pass=(bC8LcLh2WuHtJKE7r4D2 LZB33eeKa7rhz2PeDjNb)

for i in {0..1}; do
  useradd -g sftp_users -d /backup -s /sbin/nologin "${users[i]}"
  echo "${users[i]}":"${pass[i]}" | chpasswd
  mkdir -p "/data/${users[i]}/backup"
  chmod o-rx "/data/${users[i]}/backup"
  chmod o-rx "/data/${users[i]}"
  chown -R root:sftp_users "/data/${users[i]}"
  chown -R "${users[i]}":admin "/data/${users[i]}/backup"
done

systemctl restart sshd

# Rsyslog
apt update
apt install rsyslog-gnutls -y
cp ./backupserver/rsyslog.conf /etc/rsyslog.conf
systemctl restart rsyslog
