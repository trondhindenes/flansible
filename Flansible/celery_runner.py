from celery import Celery
from ConfigParser import SafeConfigParser


class Runner:
    def __init__(celery):
        celery = celery
    
    @celery.task(bind=True, soft_time_limit=task_timeout, time_limit=(task_timeout+10))
    def do_long_running_task(self, cmd):
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

        
            #Thread(target=stream_watcher, name='stdout-watcher',
            #        args=('STDOUT', proc.stdout)).start()
            #Thread(target=stream_watcher, name='stderr-watcher',
            #        args=('STDERR', proc.stderr)).start()

            #while True:
            #    print("Waiting for output")
            #    try:
            #        # Block for 1 second.
            #        item = io_q.get(True, 0.3)
            #    except Empty:
            #        if proc.poll() is not None:
            #            #Task is done, end loop
            #            break
            #    else:
            #        identifier, line = item
            #        print identifier + ':', line
            #        if identifier == "STDERR":
            #            has_error = True
            #        output = output + line
            #        self.update_state(state='PROGRESS',
            #                  meta={'result': output})
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
                            'description': "Celery ran the task, but ansible reported error"
                        }
                self.update_state(state='FAILED',
                              meta=meta)
            if len(output) is 0:
                output = "no output, maybe no matching hosts?"
                meta = {'output': output, 
                            'returncode': return_code,
                            'description': "Celery ran the task, but ansible reported error"
                        }
            return meta