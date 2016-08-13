import os
from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flask_restful import reqparse
from flansible import app
from flansible import api, app, celery, auth, ansible_default_inventory, get_inventory_access, task_timeout
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
import celery_runner
from flansible_git import FlansibleGit

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
        do_update_git_repo = args['update_git_repo']

        if do_update_git_repo is True:
            result = FlansibleGit.update_git_repo(playbook_dir)
            task = celery_runner.do_long_running_task.AsyncResult(result.id)
            while task.state == "PENDING" or task.state == "PROGRESS":
                #waiting for finish
                task = celery_runner.do_long_running_task.AsyncResult(result.id)
            if task.result['returncode'] != 0:
                #git update failed
                resp = app.make_response((str.format("Failed to update git repo: {0}", playbook_dir), 404))
                return resp

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
        task_result = celery_runner.do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        result = {'task_id': task_result.id}
        return result


api.add_resource(RunAnsiblePlaybook, '/api/ansibleplaybook')