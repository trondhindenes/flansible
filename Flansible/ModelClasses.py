from flask_restful_swagger import swagger
from flask_restful import Resource, Api, reqparse, fields, marshal_with


@swagger.model
class AnsibleExtraArgsModel:
    resource_fields = {
        'arg_name' : fields.String,
        'arg_value' : fields.String,
        }

@swagger.model
@swagger.nested(
   module_args=AnsibleExtraArgsModel.__name__,
   extra_vars=AnsibleExtraArgsModel.__name__)
class AnsibleCommandModel:
    resource_fields = {
        'host_pattern': fields.String,
        'module': fields.String,
        'module_args': fields.List(fields.Nested(AnsibleExtraArgsModel.resource_fields)),
        'extra_vars': fields.List(fields.Nested(AnsibleExtraArgsModel.resource_fields)),
        'inventory': fields.String,
        'forks' : fields.Integer,
        'verbose_level': fields.Integer,
        'become': fields.Boolean,
        'become_method': fields.String,
        'become_user': fields.String,
    }

@swagger.model
@swagger.nested(
   module_args=AnsibleExtraArgsModel.__name__,
   extra_vars=AnsibleExtraArgsModel.__name__)
class AnsiblePlaybookModel:
    resource_fields = {
        'playbook_dir': fields.String,
        'playbook': fields.String,
        'inventory': fields.String,
        'extra_vars': fields.List(fields.Nested(AnsibleExtraArgsModel.resource_fields)),
        'forks' : fields.Integer,
        'verbose_level': fields.Integer,
        'become': fields.Boolean,
    }



@swagger.model
class AnsibleRequestResultModel:
    def __init__(self, task_id):
        pass