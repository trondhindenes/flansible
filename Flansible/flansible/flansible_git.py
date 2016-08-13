from flansible import task_timeout
import celery_runner

class FlansibleGit:
    @staticmethod
    def update_git_repo(playbook_dir, remote_name='origin',branch_name='master', reset=False):

        if reset:
            command = str.format("cd {0};git fetch {1} {2};git reset --hard {1}/{2};git pull {1} {2}", playbook_dir, remote_name, branch_name)
        else:
            command = str.format("cd {0};git pull {1} {2}", playbook_dir, remote_name, branch_name)
        task_result = celery_runner.do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        return task_result