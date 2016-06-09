#Flansible
### A super-simple rest api for Ansible

---

Flansible is a very simple rest api for executing Ansible ad-hoc-commands and (later) playbooks. It it _not_ a replacement for [Ansible Tower](https://www.ansible.com/tower).

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

### Setup
Setup tested on Ubuntu 14.04
from the Flansible/Flansible directory (where the .py files live), run the following (either using [screen](http://aperiodic.net/screen/start) or in separate terminals):

`celery worker -A app.celery --loglevel=info` (this starts the celery worker which will actually execute the things)

`python app.py` (this starts the actual webserver. You're free to replace the built-in flask server with something else)

OPTIONAL: `flower --broker=redis://localhost:6379/0` (this starts the flower web gui, which gives provides information for running tasks. Replace the value of `--broker` with your own connection string for the redis/rabbitmq data store)

### Usage: General
Flansible comes with swagger documentation, which can be reached at
`http://<hostname>/api/spec.html`, with the json spec located at `http://<hostname>/api/spec`

### Usage: Ad-hoc commands
Issue a POST to `http://<hostname>/api/ansiblecommand` with contenttype `Application/Json`.

Flansible uses basic auth, with username/password configurable in the config.ini file (default: admin/admin)
The body should contain the following (also, see the swagger spec mentioned above):
```json
{                                               
    "module":  "find",
    "host_filter": "localhost",
    "extra_args":  {                            
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
TODO




