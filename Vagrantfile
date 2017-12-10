# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "gbarbieru/xenial"
  config.vm.network :forwarded_port, guest: 3000, host: 3000
  config.vm.network :forwarded_port, guest: 80, host: 3001
  config.vm.network :forwarded_port, guest: 5555, host: 3002
  config.vm.provision "shell", path: "Flansible/Utils/vagrant_setup.sh"

end
