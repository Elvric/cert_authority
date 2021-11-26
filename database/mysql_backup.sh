#!/bin/bash

mysqldump --database imovies users > databaseBackupFile.sql #TODO: backup name: backup name + date, to keep all backups
export SSHPASS=bC8LcLh2WuHtJKE7r4D2
sshpass -e sftp -oBatchMode=no dbackup@ #TODO: generate ssh pk
