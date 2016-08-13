from flask_restful import Resource, Api, reqparse, fields

class test_route(Resource):
    def post(self):
        return "hello"