## Vagrant support for nauta

### Disclaimer 

* **This is only for nauta evaluation purposes, do not use on production**
* IvyBridge processors are not fully supported by VirtualBox; F16c, FMA, BMI, AVX2 features are disabled: https://www.virtualbox.org/ticket/17745 - inference may not work

### Useful links:

* https://www.vagrantup.com/docs/index.html - Vagrant documentation
* https://www.virtualbox.org/wiki/Documentation - VirtualBox documentation
* https://github.com/intelai/nauta - Nauta

### Installation guide

#### Prerequisits

* For futher steps you will need to have installed Vagrant and VirtualBox on your host.
* You have to install plugins to vagrant:
  * vagrant-proxyconf if system is using proxy: http://tmatilai.github.io/vagrant-proxyconf/
  * vagrant-disksize
* Nauta compiled package from https://github.com/NervanaSystems/nauta
* RSA key for platform ssh


#### Installation

1. Please create vagrant and vagrant-files directories
2. To vagrant directory please download - https://github.com/IntelAI/nauta/tree/develop/toolbox/providers/vagrant/virtualbox
3. Copy:
  * nauta compiled package content to vagrant-files directory and unpack it to nauta-vagrant
  * inventory from: https://github.com/IntelAI/nauta/tree/develop/toolbox/providers/vagrant/virtualbox to nauta-vagrant
  * config.yml from: https://github.com/IntelAI/nauta/tree/develop/toolbox/providers/vagrant/virtualbox to nauta-vagrant
  * If you have proxy please set up proxy in config.yml
4. Copy RSA private and public key to vagrant-files directory
5. Copy disk-extend.sh script to vagrant-files directory
6. Configure Vagrantfile in vagrant directory:
  * You need to set up those variables

  ```
  storage_disk = 'c:\vagrant-files\secondDisk.vdi' # where the virtual disk will be created
  storage_script = 'c:\vagrant-files\disk-extend.sh' # where the disk-extend script has landed
  http_proxy="http://proxy.example.com:123" # proxy if used, else leave blank
  https_proxy="https://proxy.example.com:123" # proxy if used, else leave blank
  no_proxy="localhost,127.0.0.1,.nauta,192.168.0.0/8,10.0.0.0/8" # no_proxy if used, else leave blank
  nauta_installer="c:/vagrant-files/nauta-vagrant" # path to nauta compiled package 
  nauta_private_ssh_key="c:/vagrant-files/id_rsa" # path to private RSA key used on platform
  nauta_public_ssh_key="c:/vagrant-files/id_rsa.pub" # path to public RSA key used on platform
  ```
7. Run `vagrant validate` in vagrant directory 
8. Run `vagrant up` in vagrant directory and wait for process to end
9. ssh to the jumphost `vagrant ssh jumphost`
10. Login to nauta user `sudo su nauta`
11. Go to nauta-vagrant directory at /home/nauta/nauta-vagrant
12. Run `./installer.sh install`
13. Wait for process to end. Nauta has been installed.

