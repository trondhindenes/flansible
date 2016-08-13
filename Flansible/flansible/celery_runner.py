from celery import Celery
import subprocess
from subprocess import Popen, PIPE
from flansible import api, app, celery, task_timeout



@celery.task(bind=True, soft_time_limit=task_timeout, time_limit=(task_timeout+10))
def do_long_running_task(self, cmd, type='Ansible'):
    with app.app_context():
        
        has_error = False
        result = None
        output = ""
        self.update_state(state='PROGRESS',
                          meta={'output': output, 
                                'description': "",
                                'returncode': None})
        print(str.format("About to execute: {0}", cmd))
        proc = Popen([cmd], stdout=PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in iter(proc.stdout.readline, ''):
            print(str(line))
            output = output + line
            self.update_state(state='PROGRESS', meta={'output': output,'description': "",'returncode': None})

        return_code = proc.poll()
        if return_code is 0:
            meta = {'output': output, 
                        'returncode': proc.returncode,
                        'description': ""
                    }
            self.update_state(state='FINISHED',
                              meta=meta)
        elif return_code is not 0:
            #failure
            meta = {'output': output, 
                        'returncode': return_code,
                        'description': str.format("Celery ran the task, but {0} reported error", type)
                    }
            self.update_state(state='FAILED',
                          meta=meta)
        if len(output) is 0:
            output = "no output, maybe no matching hosts?"
            meta = {'output': output, 
                        'returncode': return_code,
                        'description': str.format("Celery ran the task, but {0} reported error", type)
                    }
        return meta
