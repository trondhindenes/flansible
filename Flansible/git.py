import platform
import os
import time
import sys
import json
from threading import Thread
from subprocess import Popen, PIPE
import subprocess
from Queue import Queue, Empty
from datetime import datetime
from ConfigParser import SafeConfigParser
from flask import render_template
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, reqparse, fields
from flask_restful_swagger import swagger
import celery.events.state
from celery import Celery

from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel

import flansible_git



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
        }
    ])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('playbook_dir', type=str, help='folder where playbook file resides', required=True)
        args = parser.parse_args()
        playbook_dir = args['playbook_dir']
        task_result = flansible_git.FlansibleGit.update_git_repo(playbook_dir)
        result = {'task_id': task_result.id}
        return result