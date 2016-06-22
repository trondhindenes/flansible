#Flansible
### A super-simple rest api for Ansible

---

Flansible is a very simple rest api for executing Ansible ad-hoc-commands and playbooks. It it _not_ a replacement for [Ansible Tower](https://www.ansible.com/tower).

Flansible is written in [Flask](http://flask.pocoo.org/), and uses [celery](http://www.celeryproject.org/) for async task execution and optionally [flower](http://flower.readthedocs.io/en/latest/features.html) for real-time monitoring of celery.

#### Required python packages with tested versions (newer version should be fine):
```bash
ansible==2.1.0.0
celery==3.1.23
Flask==0.10.1
Flask-HTTPAuth==3.1.2
Flask-RESTful==0.3.5
flask-restful-swagger==0.19
flower==0.9.1
redis==2.10.5
```

#### Other things:
Celery requires a datastore, either Redis or RabbitMQ.

#### Configuration
The config.ini file should be pretty self-explanatory. It's probably a good idea to remove lines 5-10 in app.py, as that's only a debug definition which probably won't make sense to you.

If you want to run the flask webserver on port 80 like I'm doing without running as root, you need to allow python to use priveliged ports:

`sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python2.7`

### Setup
Setup tested on Ubuntu 14.04

from the Flansible/Flansible directory (where the .py files live), run the following (either using [screen](http://aperiodic.net/screen/start) or in separate terminals):

`celery worker -A app.celery --loglevel=info` (this starts the celery worker which will actually execute the things)

`python app.py` (this starts the actual webserver. You're free to replace the built-in flask server with something else)

OPTIONAL: `flower --broker=redis://localhost:6379/0` (this starts the flower web gui, which gives provides information for running tasks. Replace the value of `--broker` with your own connection string for the redis/rabbitmq data store). Flower will be available on `http://<hostname>:5555`.

### Usage: General
Flansible comes with swagger documentation, which can be reached at
`http://<hostname>/api/spec.html`, with the json spec located at `http://<hostname>/api/spec`. This should be your first stop for getting to know the 
expected json payload when interacting with the api.

### Usage: Role-based access
Flansible uses basic auth, with username/password configurable in the rbac.json file (default: admin/admin)

rbac.json allows linking usernames with a list of allowed inventories. The example provided shows how to configure a "devadmin" user
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

### Usage: Ad-hoc commands
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

### Usage: Playbooks
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

### Usage: Getting status
both ansibleplaybook and ansiblecommand will return a task_id value. That value can be used to check the 
status and output of the job. This is done by issuing a GET to 
`http://<hostname>/api/ansibletaskstatus/<task_id>` with contenttype `Application/Json`.

### Usage: Getting output
The output of the ansible command/playbook can be viewed live while the task is running, and afterwards.
Issue a GET cal to:
`http://<hostname>/api/ansibletaskoutput/<task_id>` with contenttype `Application/Json`.
The output from this call should resemble what you see in bash when executing Ansible interactively.

### how it looks
* Execute an Ansible command (`/api/ansiblecommand`). The returning task_id is used to check status: 

![alt text](http://s33.postimg.org/eucfmo0un/2016_06_09_03_12_32_Postman.jpg "Execute the thing")

* Use the returned task_id to get the Ansible job output (`/api/ansibletaskoutput/<task-id>`):

![alt text](http://s33.postimg.org/7ir75l7wv/2016_06_09_03_13_04_Postman.jpg "Get output")

* Use Flower to check job statuses:

![alt text](http://s33.postimg.org/wnn9g4dov/2016_06_09_03_19_09_Celery_Flower.png "Get job status")

* Use Swagger to get a feel for the api (this is very much work in progress):

![alt text](http://s33.postimg.org/fq2hivpe7/2016_06_09_03_20_49_Swagger_UI.png "Swagger spec")






