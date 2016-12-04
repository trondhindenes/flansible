systemctl disable apt-daily.service
systemctl disable apt-daily.timer
apt-get update
apt-get install build-essential -y
apt-get install git python-setuptools python-dev sshpass libffi-dev libssl-dev make libxml2-dev libxslt1-dev acl -y
easy_install pip
pip install paramiko PyYAML jinja2 httplib2 requests lxml cssselect xmltodict
pip install pywinrm
pip install requests --upgrade
mkdir -p /opt/ansible
cd /opt/ansible
git clone git://github.com/ansible/ansible.git --recursive
cd /opt/ansible/ansible
make
make install
cd /vagrant/playbook
ansible-playbook site.yml
setcap 'cap_net_bind_service=+ep' /usr/bin/python2.7

