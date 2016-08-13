import os
from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flask_restful import reqparse
from flansible import app
from flansible import api, app, auth, ansible_default_inventory, get_inventory_access, task_timeout
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
import celery_runner

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
        task_result = celery_runner.do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        result = {'task_id': task_result.id}
        return result

api.add_resource(RunAnsibleCommand, '/api/ansiblecommand')
