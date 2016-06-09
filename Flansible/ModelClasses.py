from flask_restful_swagger import swagger
from flask_restful import Resource, Api, reqparse, fields, marshal_with


@swagger.model
class AnsibleExtraArgsModel:
    resource_fields = {
        'arg_name' : fields.String,
        'arg_value' : fields.String,
        }

@swagger.model
class AnsibleCommandModel:
    resource_fields = {
        'module': fields.String,
        'extra_args': fields.List(fields.Nested(AnsibleExtraArgsModel.resource_fields)),
        'inventory': fields.String,
        'forks' : fields.Integer,
        'verbose_level': fields.Integer,
    }



@swagger.model
class AnsibleRequestResultModel:
    def __init__(self, task_id):
        pass