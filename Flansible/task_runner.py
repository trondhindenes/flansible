from celery import Celery

app = Celery('task_runner', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@Celery.task(app)
def do_long_running_task(self):
    with app.app_context():
        self.update_state(state='PROGRESS',
                          meta={'current': 1, 'total': 1,
                                'status': "yup"})
        time.sleep(3)
        error_out = None
        result = None
        try:
            result = subprocess.check_output(["source ~/ansible/ansible/hacking/env_setup", "ansible --version"], shell=True, stderr=error_out)
        except Exception as e:
            error_out = str(e)

        self.update_state(state='PROGRESS',
                          meta={'current': 1, 'total': 1,
                                'status': result})
        if error_out:
            #failure
            return {'current': 1, 'total': 1, 'status': 'Failure!',
                    'result': error_out}
        else:
            return {'current': 1, 'total': 1, 'status': 'Task completed!',
                    'result': result}