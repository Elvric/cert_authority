#!/bin/bash

curr_date=`date + "%Y-%m-%d"`

mysqldump --database imovies users > backups/imovies_users_bkp_$curr_date.sql
sftp -i ssh_keys/db_priv_key dbackup@172.27.0.4 << !
put backups/imovies_users_bkp_$curr_date.sql db_backups/
quit
!
