# MOVE YOUR VENV from caserver/api to caserver 
otherwise vagrant will try to copy it to the CA VM (taking too much time)

# Installing Vagrant
Follow this [link](https://www.vagrantup.com/downloads) and your wishes shall
be granted


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

### Database
Seem to work fine, no problem there

### CaServer
Seem to work fine, no problem there

### Webserver
Ran into some issues when building the project

## Things that need to be done before submitting the project
- Check all the TODOs in the project then do `vagrant destroy` `vagrant up`
- Change the vagrant user to admin user with a hard password
- Disable ssh vagrant
- Disable the no password sudo property of the vagrant user
