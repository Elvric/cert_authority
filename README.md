# MOVE YOUR VENV from caserver/api to caserver 
otherwise vagrant will try to copy it to the CA VM (taking too much time)


# Virtual Machines and Vagrant
When running vagrant ensure that you are in the root directory of this project.
All the setup is in the `Vagrantfile`

`vagrant up` spawns all the VMs  
`vagrant up [name]` only spawns the VM mentioned  
`vagrant destroy` destroys the VM similar to `docker-compose down`  
`vagrant destroy [name]` only destroys the VM mentioned  
`vagrant provision` run all the provision commands in the `VagrantFile`  
`vagrant provision [name]` only runs the provision of the machine specified
`vagrant status` shows you what services are currently running

`vagrant ssh [name]` ssh you inside the VM mentioned,

**You can also see the VMs by opening virtual box**

## TODOS
Note that currently the services do not work

### Database
Seem to work fine, no problem there

### CaServer
Ran into some issues with Json tokens not sure why to be reviewed

### Webserver
Ran into some issues when building the project
