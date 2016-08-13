from celery_runner import Runner

class FlansibleGit:
    @staticmethod
    def update_git_repo(playbook_dir):

        runner = Runner()

        remote_name = "origin"
        branch_name = "master"
        command = str.format("cd {0};git pull {1} {2}", playbook_dir, remote_name, branch_name)
        task_result = runner.do_long_running_task.apply_async([command], soft=task_timeout, hard=task_timeout)
        return task_result