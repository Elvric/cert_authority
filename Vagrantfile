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
    caserver.vm.network "forwarded_port", guest: 443, host: 8083
  end

config.vm.define "webserver" do |wb|
    wb.vm.box = OS
    wb.vm.provision "file", source: "./webserver/cert", destination: "webserver/cert"
    wb.vm.provision "file", source: "./webserver/nginx", destination: "webserver/nginx"
    wb.vm.provision "file", source: "./webserver/frontend/src", destination: "webserver/frontend/src"
    wb.vm.provision "file", source: "./webserver/frontend/public", destination: "webserver/frontend/public"
    wb.vm.provision "file", source: "./webserver/frontend/package.json", destination: "webserver/frontend/package.json"
    wb.vm.provision "file", source: "./webserver/frontend/package-lock.json", destination: "webserver/frontend/package-lock.json"
    wb.vm.provision "shell", path: "./webserver/setup_webserver.sh"
    wb.vm.network "private_network", ip: "172.26.0.2", virtualbox__intnet: "dmz"
    wb.vm.network "forwarded_port", guest: 443, host: 4443
  end

  config.vm.define "backupserver" do |bk|
    bk.vm.box = OS
    wb.vm.provision "shell", path: "./backupserver/setup_webserver.sh"
    caserver.vm.network "private_network", ip: "172.27.0.4", virtualbox__intnet: "internal_net"
  end

 config.vm.define "firewall" do |fr|
    fr.vm.box = OS
    fr.vm.provision "shell", path: "./firewall/setup_firewall.sh"
    fr.vm.network "private_network", ip: "172.27.0.254", virtualbox__intnet: "internal_net"
    fr.vm.network "private_network", ip: "172.26.0.254", virtualbox__intnet: "dmz"
  end
end
