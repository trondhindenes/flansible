from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flansible import app
from flansible import api, app, celery, auth
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
import celery_runner

class git(Resource):
    @swagger.operation(
    notes='Update git repo on disk',
    nickname='updategit',
    parameters=[
        {
        "name": "playbook_dir",
        "description": "The git dir to update",
        "required": True,
        "allowMultiple": False,
        "dataType": 'string',
        "paramType": "body"
        },
        {
        "name": "remote_name",
        "description": "git remote name. defaults to origin",
        "required": False,
        "allowMultiple": False,
        "dataType": 'string',
        "paramType": "body"
        },
        {
        "name": "branch_name",
        "description": "git branch name. defaults to master",
        "required": False,
        "allowMultiple": False,
        "dataType": 'string',
        "paramType": "body"
        },
        {
        "name": "reset",
        "description": "perform a hard reset on the repo",
        "required": False,
        "allowMultiple": False,
        "dataType": 'bool',
        "paramType": "body"
        },
    ])
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('playbook_dir', type=str, help='folder where playbook file resides', required=True)
        parser.add_argument('remote_name', type=str, help='remote name', required=False)
        parser.add_argument('branch_name', type=str, help='branch name', required=False)
        parser.add_argument('reset', type=bool, help='hard reset', required=False)
        args = parser.parse_args()
        playbook_dir = args['playbook_dir']
        remote_name = args['remote_name']
        branch_name = args['branch_name']
        reset = args['reset']

        if not remote_name:
            remote_name = 'origin'
        if not branch_name:
            branch_name = 'master'
        if not reset:
            reset = False

        task_result = update_git_repo(playbook_dir, remote_name, branch_name, reset)
        result = {'task_id': task_result.id}
        return result

api.add_resource(git, '/api/git')
