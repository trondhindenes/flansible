import platform

#Visual studio remote debugger
if platform.node() == 'thansible01':
    try:
        import ptvsd
        ptvsd.enable_attach(secret='my_secret', address = ('0.0.0.0', 3000))
    except:
        pass

import os
from datetime import datetime
from flask import render_template
from celery import Celery
import subprocess
import time
from flask_restful import Resource, Api
from ConfigParser import SafeConfigParser
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
from celery import Celery
import celery.events.state
import subprocess
import time
from flask_restful import Resource, Api, reqparse, fields
from flask_restful_swagger import swagger
import sys
import json
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
from flansible_git import FlansibleGit



app = Flask(__name__)
auth = HTTPBasicAuth()

this_path = sys.path[0]

config = SafeConfigParser()
config.read('config.ini')

ansible_config = SafeConfigParser()
try:
    ansible_config.read('/etc/ansible/ansible.cfg')
    ansible_default_inventory = config.get("Defaults", "inventory")
except:
    ansible_default_inventory = '/etc/ansible/hosts'

app.config['CELERY_BROKER_URL'] = config.get("Default", "CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = config.get("Default", "CELERY_RESULT_BACKEND")
str_task_timeout = config.get("Default", "CELERY_TASK_TIMEOUT")
task_timeout = int(str_task_timeout)

api = swagger.docs(Api(app), apiVersion='0.1')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], )
celery.control.time_limit('do_long_running_task', soft=900, hard=900, reply=True)
celery.conf.update(app.config)

inventory_access = []

def get_inventory_access(username, inventory):
    if username == "admin":
        return True
    result = False
    with open("rbac.json") as rbac_file:
        rbac_data = json.load(rbac_file)
    user_list = rbac_data['rbac']
    for user in user_list:
        if user['user'] == username:
            inventory_list = user['inventories']
            if inventory in inventory_list:
                result = True
    return result

@auth.verify_password
def verify_password(username, password):
    result = False
    with open("rbac.json") as rbac_file:
        rbac_data = json.load(rbac_file)
    user_list = rbac_data['rbac']
    for user in user_list:
        if user['user'] == username:
            if user['password'] == password:
                result = True
                inventory_access = user['inventories']
    return result

class RunAnsibleCommand(Resource):
    @swagger.operation(
        notes='Run ad-hoc Ansible command',
        nickname='ansiblecommand',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
              "name": "body",
              "description": "Inut object",
              "required": True,
              "allowMultiple": False,
              "dataType": AnsibleCommandModel.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 200,
              "message": "Ansible command started"
            },
            {
              "code": 400,
              "message": "Invalid input"
            }
          ]
    )
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('host_pattern', type=str, help='need to specify host_pattern', required=True)
        parser.add_argument('module', type=str, help='module name', required=True)
        parser.add_argument('module_args', type=dict, help='module_args', required=False)
        parser.add_argument('extra_vars', type=dict, help='extra_vars', required=False)
        parser.add_argument('inventory', type=str, help='path to inventory', required=False,)
        parser.add_argument('forks', type=int, help='forks', required=False)
        parser.add_argument('verbose_level', type=int, help='verbose level, 1-4', required=False)
        parser.add_argument('become', type=bool, help='run with become', required=False)
        parser.add_argument('become_method', type=str, help='become method', required=False)
        parser.add_argument('become_user', type=str, help='become user', required=False)
        args = parser.parse_args()
        host_pattern = args['host_pattern']
        req_module = args['module']
        module_args = args['module_args']
        extra_vars = args['extra_vars']
        inventory = args['inventory']
        forks = args['forks']
        verbose_level = args['verbose_level']
        become = args['become']
        become_method = args['become_method']
        become_user = args['become_user']
        module_args_string = ''
        extra_vars_string = ''
        curr_user = auth.username()
        
        if module_args:
            counter = 1
            module_args_string += '-a"'
            for key in module_args.keys():
                if counter < len(module_args):
                    spacer = " "
                else:
                    spacer = ""
                opt_string = str.format("{0}={1}{2}",key,module_args[key], spacer)
                module_args_string += opt_string
                counter += 1
            module_args_string += '"'

        if extra_vars:
            counter = 1
            extra_vars_string += ' -e"'
            for key in extra_vars.keys():
                if counter < len(extra_vars):
                    spacer = " "
                else:
                    spacer = ""
                opt_string = str.format("{0}={1}{2}",key,extra_vars[key], spacer)
                extra_vars_string += opt_string
                counter += 1
            extra_vars_string += '"'
        
        if not inventory:
            inventory = ansible_default_inventory
            has_inv_access =  get_inventory_access(curr_user,  inventory)
            if not has_inv_access:
                resp = app.make_response((str.format("User does not have access to inventory {0}", inventory), 403))
                return resp

        inventory = str.format(" -i {0}", inventory)
        if forks:
            fork_string = str.format('-f {0}', str(forks))
        else:
            fork_string = ''

        if verbose_level and verbose_level != 0:
            verb_counter = 1
            verb_string = " -"
            while verb_counter <= verbose_level:
                verb_string += "v"
                verb_counter += 1
        else:
            verb_string = ''

        if become:
            become_string = ' --become'
        else:
            become_string = ''

        if become_method:
            become_method_string = str.format(' --become-method={0}', become_method)
        else:
            become_method_string = ''

        if become_user:
            become_user_string = str.format(' --become-user={0}', become_user)
        else:
            become_user_string = ''


        command = str.format("ansible {9} -m {0} {1} {2} {3}{4}{5}{6}{7}{8}", req_module, module_args_string, fork_string, verb_string, 
                             become_string, become_method_string, become_user_string, inventory, extra_vars_string ,host_pattern)
        task_result = do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        result = {'task_id': task_result.id}
        return result

api.add_resource(RunAnsibleCommand, '/api/ansiblecommand')


class RunAnsiblePlaybook(Resource):
    @swagger.operation(
        notes='Run Ansible Playbook',
        nickname='ansibleplaybook',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
              "name": "body",
              "description": "Inut object",
              "required": True,
              "allowMultiple": False,
              "dataType": AnsiblePlaybookModel.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 200,
              "message": "Ansible playbook started"
            },
            {
              "code": 400,
              "message": "Invalid input"
            }
          ]
    )
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('playbook_dir', type=str, help='folder where playbook file resides', required=True)
        parser.add_argument('playbook', type=str, help='name of the playbook', required=True)
        parser.add_argument('inventory', type=str, help='path to inventory', required=False,)
        parser.add_argument('extra_vars', type=dict, help='extra vars', required=False)
        parser.add_argument('forks', type=int, help='forks', required=False)
        parser.add_argument('verbose_level', type=int, help='verbose level, 1-4', required=False)
        parser.add_argument('become', type=bool, help='run with become', required=False)
        parser.add_argument('update_git_repo', type=bool, help='Set to true to update git repo prior to executing', required=False)
        args = parser.parse_args()

        playbook_dir = args['playbook_dir']
        playbook = args['playbook']
        become = args['become']
        inventory = args['inventory']
        update_git_repo = args['update_git_repo']

        if update_git_repo is True:
            playbook_dir, playbook = FlansibleGit.update_git_repo(playbook_dir, playbook)

        curr_user = auth.username()
        
        playbook_full_path = playbook_dir + "/" + playbook
        playbook_full_path = playbook_full_path.replace("//","/")

        if not os.path.exists(playbook_dir):
            resp = app.make_response((str.format("Directory not found: {0}", playbook_dir), 404))
            return resp
        if not os.path.isdir(playbook_dir):
            resp = app.make_response((str.format("Not a directory: {0}", playbook_dir), 404))
            return resp
        if not os.path.exists(playbook_full_path):
            resp = app.make_response((str.format("Playbook not found in folder. Path does not exist: {0}", playbook_full_path), 404))
            return resp

        if not inventory:
            inventory = ansible_default_inventory
            has_inv_access =  get_inventory_access(curr_user,  inventory)
            if not has_inv_access:
                resp = app.make_response((str.format("User does not have access to inventory {0}", inventory), 403))
                return resp

        inventory = str.format(" -i {0}", inventory)

        if become:
            become_string = ' --become'
        else:
            become_string = ''


        command = str.format("cd {0};ansible-playbook {1}{2}{3}", playbook_dir, playbook, become_string, inventory)
        task_result = do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        result = {'task_id': task_result.id}
        return result


api.add_resource(RunAnsiblePlaybook, '/api/ansibleplaybook')
    
class AnsibleTaskOutput(Resource):
    @swagger.operation(
    notes='Get the output of an Ansible task/job',
    nickname='ansibletaskoutput',
    parameters=[
        {
        "name": "task_id",
        "description": "The ID of the task/job to get status for",
        "required": True,
        "allowMultiple": False,
        "dataType": 'string',
        "paramType": "path"
        }
    ])
    @auth.login_required
    def get(self, task_id):
        task = do_long_running_task.AsyncResult(task_id)
        
        if task.state == "PROGRESS":
            result = "Task in progress"
        else:
            result = task.info['result']
        #result_out = task.info.replace('\n', "<br>")
        #result = result.replace('\n', '<br>')
        #return result, 200, {'Content-Type': 'text/html; charset=utf-8'}
        resp = app.make_response((result, 200))
        resp.headers['content-type'] = 'text/plain'
        return resp

api.add_resource(AnsibleTaskOutput, '/api/ansibletaskoutput/<string:task_id>')

class AnsibleTaskStatus(Resource):
    @swagger.operation(
    notes='Get the status of an Ansible task/job',
    nickname='ansibletaskstatus',
    parameters=[
        {
        "name": "task_id",
        "description": "The ID of the task/job to get status for",
        "required": True,
        "allowMultiple": False,
        "dataType": 'string',
        "paramType": "path"
        }
    ])
    @auth.login_required
    def get(self, task_id):
        task = do_long_running_task.AsyncResult(task_id)
        result_obj = {'Status': task.state}
        return  result_obj

api.add_resource(AnsibleTaskStatus, '/api/ansibletaskstatus/<string:task_id>')

@celery.task(bind=True, soft=task_timeout, hard=(task_timeout+10))
def do_long_running_task(self, cmd):
    with app.app_context():
        error_out = None
        result = None
        self.update_state(state='PROGRESS',
                          meta={'result': result})
        try:
            result = subprocess.check_output([cmd], shell=True, stderr=error_out)
        except Exception as e:
            error_out = str(e)

        self.update_state(state='FINISHED',
                          meta={'result': error_out})
        if error_out:
            #failure
            self.update_state(state='FAILED',
                          meta={'result': error_out})
            return {'result': error_out}
        else:
            if len(result) is 0:
                result = "no output, maybe no matching hosts?"
            return {'result': result}

if __name__ == '__main__':
    app.run(debug=True, host=config.get("Default", "Flask_tcp_ip"), use_reloader=False, port=int(config.get("Default", "Flask_tcp_port")))