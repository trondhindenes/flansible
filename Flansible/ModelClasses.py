from flask_restful_swagger import swagger

@swagger.model
class AnsibleCommandModel:
    resource_fields = {
        'module': fields.String,
        'extra_args': fields.Nested(AnsibleExtraArgsModel.resource_fields),
    }

class AnsibleExtraArgsModel:
    resource_fields = {
        'arg_name' : fields.String,
        'arg_value' : fields.String,
        }

@swagger.model
class AnsibleRequestResultModel:
    def __init__(self, task_id):
        pass