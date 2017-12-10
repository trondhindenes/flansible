FROM ubuntu:14.04.1
RUN apt-get update && \
    apt-get install --no-install-recommends -y software-properties-common && \
    apt-add-repository ppa:ansible/ansible && \
    apt-get update && \
    apt-get install -y ansible python-pip git openssh-server apache2 \
                       redis-server libapache2-mod-wsgi build-essential \
                       python-setuptools python-dev sshpass libffi-dev \
                       libssl-dev make libxml2-dev libxslt1-dev acl

RUN pip install git+git://github.com/ansible/ansible.git@devel
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN echo '[local]\nlocalhost ansible_connection=ssh ansible_ssh_user=root ansible_ssh_pass=admin\n' > /etc/ansible/hosts
RUN sed -i 's/#host_key_checking/host_key_checking/g' /etc/ansible/ansible.cfg

# https://docs.docker.com/engine/examples/running_ssh_service/
RUN mkdir /var/run/sshd
RUN echo 'root:admin' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

