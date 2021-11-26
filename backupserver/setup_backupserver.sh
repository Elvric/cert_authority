#!/bin/bash
cat <<EOF >> /etc/ssh/sshd_config
Match Group sftp_users
  ChrootDirectory /data/%u
  ForceCommand internal-sftp -u 0227 -P remove,rmdir
EOF
mkdir -p /data
chmod 701 /data
groupadd sftp_users
groupadd admin
users=(dbackup cabackup)
pass=(bC8LcLh2WuHtJKE7r4D2 admin)

for i in {0..0}; do
  useradd -g sftp_users -d /backup -s /sbin/nologin "${users[i]}"
  echo "${users[i]}":"${pass[i]}" | chpasswd
  mkdir -p "/data/${users[i]}/backup"
  chmod o-rx "/data/${users[i]}/backup"
  chmod o-rx "/data/${users[i]}"
  chown -R root:sftp_users "/data/${users[i]}"
  chown -R "${users[i]}":admin "/data/${users[i]}/backup"
done

# link SSH public keys to users
cat usrs_pub_keys/db_pub_key.pub >> /home/dbbackup/.ssh/authorized_keys

systemctl restart sshd

# Rsyslog
sed -i -r "s/^#(.*imtcp.*)/\1/" /etc/rsyslog.conf
systemctl restart rsyslog
