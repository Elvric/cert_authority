# CAServer

In order to ensure that the project can run properly on all the collaborators please do
the following:

1. run `setup_project.sh`

This will install some python tools that are used to manage python environment.
At the end it will automatically create a python virtual environment under `./caserver/api/venv`
directory.

## Installing dependencies and working on the python scripts for the CA Server

Ensure you are in the correct python virtual environment at all time. To be in
the environment run `source ./caserver/api/venv/bin/activate`. From there run
`pip3 install -r requirements.txt`

# WebServer

As with the CAServer, running the `setup_project.sh` script will install the requirements to run the react webserver.
The frontend code is located in `webserver/frontend` and can be started using `npm start`.

## Backup Structure

We are going to have a private public key pair, all data that is goign to be logged
will be encrypted and sent to the backup server in this form.

The private key will be stored on the backup server to decrypt the data with a passphrase
that is known only by the sysadmin.

# The problem with tls in the db
Soo, basically we had this big problem in which the db container was using mysql version 5.7.21 that used this library called yaSSL that was shit. It has so much problems plus tls goes up to version 1.1

Now I changed it and now we are running mysql 5.7.31 with tls v1.2

Now the problem is setting up the tls connection between the db and the caserver. In particular I don't know why but the db is
failing to read the private key `db.key` that I am passing, so basically the caserver is not able to verify the certificate issued
by the db server. I will try to find a solution, but any help is super appreciated :)