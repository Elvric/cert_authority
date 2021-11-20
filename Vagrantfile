# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
OS = "generic/ubuntu2004"
Vagrant.configure("2") do |config|
  config.vm.define "database" do |db|
    db.vm.box = OS
    db.vm.provision "file", source: "./database/imovies_users.sql", destination: "imovies_users.sql"
    db.vm.provision "file", source: "./database/initdatabase.sql", destination: "initdatabase.sql"
    db.vm.provision "file", source: "./database/cert", destination: "cert"
    db.vm.provision "file", source: "./database/my.cnf", destination: "my.cnf"
    db.vm.provision "shell", path: "./database/setup_database.sh"
    db.vm.network "private_network", ip: "172.27.0.3", virtualbox__intnet: "internal_net"
  end

  config.vm.define "caserver" do |caserver|
    caserver.vm.box = OS
    caserver.vm.provision "file", source: "./caserver", destination: "caserver"
    caserver.vm.provision "shell", path: "./caserver/setup_caserver.sh"
    caserver.vm.network "private_network", ip: "172.27.0.2", virtualbox__intnet: "internal_net"
    caserver.vm.network "forwarded_port", guest: 443, host: 8080
  end

end
