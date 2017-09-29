
# Flansible

> A super-simple rest api for Ansible


Flansible is a very simple REST api for executing Ansible `ad-hoc-commands` and `playbooks`. It it _not_ a replacement for [Ansible Tower](https://www.ansible.com/tower).

Flansible is written in [Flask](http://flask.pocoo.org/), and uses [celery](http://www.celeryproject.org/) for async task execution and optionally [flower](http://flower.readthedocs.io/en/latest/features.html) for real-time monitoring of celery.


#### Credits

Joerg Lehmann: Lots of feedback and help


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
  - [Required python packages](#required-python-packages)
  - [Other things:](#other-things)
  - [Configuration](#configuration)
- [Setup](#setup)
- [Usage](#usage)
  - [General](#general)
  - [Role-based access](#role-based-access)
  - [Ansible - Ad-hoc commands](#ansible---ad-hoc-commands)
  - [Ansible Playbooks](#ansible-playbooks)
  - [Getting status](#getting-status)
  - [Getting output](#getting-output)
- [How it looks](#how-it-looks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


### Overview

#### Required python packages 

With tested versions (newer version should be fine): [`requirements.txt`](Flansible/requirements.txt)


#### Other things

`Celery` requires a running datastore, either `Redis` or `RabbitMQ`.


`Flansible` does not configure this, and expects Redis or RabbitMQ to already be running and accessible.


#### Configuration

The [`config.ini`](Flansible/config.ini) file should be pretty self-explanatory. It's probably a good idea to remove lines 5-10 in `app.py`, as that's only a debug definition which probably won't make sense to you.

If you want to run the flask webserver on port 80 like I'm doing without running as root, you need to allow python to use priveliged ports:

`sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python2.7`


### Setup

A docker-compose stack is available:


```
$ docker-compose build flansible
...


$ docker-compose up -d
Creating network "flansible_default" with the default driver
Creating flansible_redis_1 ... done
Creating flansible_base_1  ... done
Creating flansible_worker_1    ... done
Creating flansible_dashboard_1 ... done
Creating flansible_flansible_1 ... done


$ docker-compose ps
        Name                       Command               State            Ports         
----------------------------------------------------------------------------------------
flansible_base_1        python2                          Exit 0                         
flansible_dashboard_1   flower --broker=redis://re ...   Up       0.0.0.0:5555->5555/tcp
flansible_flansible_1   python runserver.py              Up       0.0.0.0:3000->3000/tcp
flansible_redis_1       docker-entrypoint.sh redis ...   Up       6379/tcp              
flansible_worker_1      celery worker -A flansible ...   Exit 1  
```

Then:
* Go over Flansible: http://127.0.0.1:3000/api/spec
* Go over Celery-Flower: http://127.0.0.1:5555/


### Usage

#### General

Flansible comes with swagger documentation, which can be reached at
`http://<hostname>/api/spec.html`, with the json spec located at `http://<hostname>/api/spec`. This should be your first stop for getting to know the expected json payload when interacting with the api.


#### Role-based access

Flansible uses basic auth, with username/password configurable in the `rbac.json` file (default: admin/admin)

`rbac.json` allows linking usernames with a list of allowed inventories. The example provided shows how to configure a "devadmin" user
which doesn't have access to Ansible's default inventory:

```json
{
  "rbac": [
    {
      "user": "admin",
      "password": "admin",
      "inventories": [
        "username admin has implicit access to all inventories",
        "no need to specify anything here"
      ]

    },
    {
      "user": "devadmin",
      "password": "devpassword",
      "inventories": [
        "/some/folder/dev",
        "/home/thadministrator/hosts"
      ]

    }

  ]
}
```

Not that the username "admin" is special, and is not subject to inventory access checking.

The idea behind this rbac implementation is to allow separate credentials for executing tasks and playbooks 
against dev/test environments without having access to make changes to production systems.


#### Ansible - Ad-hoc commands

Issue a POST to `http://<hostname>/api/ansiblecommand` with contenttype `Application/Json`.

The body should contain the following (for updated info, see the swagger spec mentioned above):
```json
{
   "host_pattern": "localhost", 
    "module":  "find",
    "module_args":  {                            
        "paths":  "/tmp",       
        "age":  "2d",
        "recurse" : true
    }                            
}    
```
where
* module: The ansible module to execute
* host_filter: The host or host filter to execute on (defaults to "localhost" if omitted)
* extra_args: array of objects containing any extra vars


#### Ansible - Playbooks

Issue a POST to `http://<hostname>/api/ansibleplaybook` with contenttype `application/Json`.

This is an example of playbook execution:

```json
{
  "playbook_dir": "/home/thadministrator",
  "playbook": "test.yml",
  "become": true
}
```

Flansible will verify that the playbook dir/file exists before submitting the job for execution.

#### Getting status

Both `ansible-playbook` and `ansible` command will return a `task_id` value. That value can be used to check the status and output of the job. This is done by issuing a GET to 

`http://<hostname>/api/ansibletaskstatus/<task_id>` with contenttype `Application/Json`.


#### Getting output

The output of the ansible command/playbook can be viewed live while the task is running, and afterwards.

Issue a GET cal to:
`http://<hostname>/api/ansibletaskoutput/<task_id>` with contenttype `Application/Json`.

The output from this call should resemble what you see in bash when executing Ansible interactively.


### How it looks

* Execute an Ansible command (`/api/ansiblecommand`). The returning task_id is used to check status: 

```bash
$ curl -i -X POST -u 'admin:admin' -H 'Content-Type: application/json' -d @examples/ansiblecommand.json http://127.0.0.1:3000/api/ansiblecommand
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 58
Server: Werkzeug/0.14.1 Python/2.7.15
Date: Mon, 13 Aug 2018 09:15:23 GMT

{
    "task_id": "b9670f6e-dab7-4095-b8bf-e7c20daf4998"
}
```

![alt text](http://s33.postimg.org/eucfmo0un/2016_06_09_03_12_32_Postman.jpg "Execute the thing")


* Use the returned task_id to get the Ansible job output (`/api/ansibletaskoutput/<task-id>`):




![alt text](http://s33.postimg.org/7ir75l7wv/2016_06_09_03_13_04_Postman.jpg "Get output")

* Use Flower to check job statuses:

![alt text](http://s33.postimg.org/wnn9g4dov/2016_06_09_03_19_09_Celery_Flower.png "Get job status")

* Use Swagger to get a feel for the api (this is very much work in progress):

![alt text](http://s33.postimg.org/fq2hivpe7/2016_06_09_03_20_49_Swagger_UI.png "Swagger spec")