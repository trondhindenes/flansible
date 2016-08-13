
from flansible import api, app, celery
from flansible import io_q

def stream_watcher(identifier, stream):
    for line in stream:
        io_q.put((identifier, line))

    if not stream.closed:
        stream.close()

def status_updater():
    while True:
        try:
            # Block for 1 second.
            item = io_q.get(True, 1)
        except Empty:
            # No output in either streams for a second. Are we done?
            if proc.poll() is not None:
                break
        else:
            identifier, line = item
            print identifier + ':', line
            update_state(state='PROGRESS',
                          meta={'result': result})

def update_git_repo(playbook_dir, remote_name='origin', branch_name='master', reset=False):

    if reset is False:
        command = str.format("cd {0};git pull {1} {2}", playbook_dir, remote_name, branch_name)
    else:
        command = str.format("cd {0};git fetch {1} {2};git reset --hard {1}/{2};git pull {1} {2}", playbook_dir, remote_name, branch_name)
    task_result = do_long_running_task.apply_async([command, 'git'], soft=task_timeout, hard=task_timeout)
    return task_result
