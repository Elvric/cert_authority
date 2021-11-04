# CAServer
In order to ensure that the project can run properly on all the collaborators please do
the following:
1. run `setup_project.sh`

This will install some python tools that are used to manage python environment.
At the end it will automatically create a python virtual environment under `./caserver/venv`
directory.

## Installing dependencies and working on the python scripts for the CA Server
Ensure you are in the correct python virtual environment at all time. To be in
the environment run `source ./caserver/venv/bin/activate`. From there run 
`pipenv update`. This will install the dependencies present under the `Pipfile`.
Use `pipenv install [dep]` to install new dependencies, or `pip3 uninstall [pkg]`
to remove packages.

**This will ensure that upon pushing and pullin we all have a working version of the 
python code with all the dependencies listed. This will also make push to production easier.**

## Backup Structure
We are going to have a private public key pair, all data that is goign to be logged
will be encrypted and sent to the backup server in this form.

The private key will be stored on the backup server to decrypt the data with a passphrase
that is known only by the sysadmin.