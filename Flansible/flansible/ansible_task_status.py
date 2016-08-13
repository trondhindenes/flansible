from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flansible import app
from flansible import api, app, celery, auth
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
import celery_runner

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
        task = celery_runner.do_long_running_task.AsyncResult(task_id)
        if task.state == 'PENDING':
            result = "Task not found"
            resp = app.make_response((result, 404))
            return resp
        elif task.state == 'PROGRESS':
            result_obj = {'Status': "PROGRESS",
                              'description': "Task is currently running",
                              'returncode': None}
        else:
            try:
                return_code = task.info['returncode']
                description = task.info['description']
                if return_code is 0:
                    result_obj = {'Status': "SUCCESS", 
                                  'description': description}
                else:
                    result_obj = {'Status': "FLANSIBLE_TASK_FAILURE",
                                  'description': description,
                                  'returncode': return_code}
            except:
                result_obj = {'Status': "CELERY_FAILURE"}

        return  result_obj

api.add_resource(AnsibleTaskStatus, '/api/ansibletaskstatus/<string:task_id>')
