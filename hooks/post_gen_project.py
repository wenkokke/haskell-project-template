#!/usr/bin/env python
import logging
import os
import shutil
import subprocess

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = os.path.realpath(os.path.curdir)


if __name__ == "__main__":

    use_test = "{{cookiecutter.use_test}}"
    use_git_init = "{{cookiecutter.use_git_init}}"
    use_pre_commit = "{{cookiecutter.use_pre_commit}}"

    # Remove test_directory if 'use_test' is not 'y':
    if use_test != "y":
        shutil.rmtree(os.path.join(PROJECT_ROOT, "{{cookiecutter.test_directory}}"))

    # Initialize a git repository if 'use_git_init' is not 'n':
    if use_git_init != "n":
        subprocess.check_call(f"git init", cwd=PROJECT_ROOT, shell=True)
        # ... with a github remote if 'use_git_init' is 'github':
        if use_git_init == "github":
            github_remote_url = "{{cookiecutter.__github_remote_url}}"
            subprocess.check_call(
                f"git remote add origin {github_remote_url}",
                cwd=PROJECT_ROOT,
                shell=True,
            )

    # Run pre-commit if 'use_pre_commit' is 'y':
    if use_pre_commit == "y":
        try:
            subprocess.check_call(
                f"pre-commit run --files ./**/*", cwd=PROJECT_ROOT, shell=True
            )
        except subprocess.CalledProcessError as e:
            LOGGER.warning(e)

    # Install pre-commit if 'use_pre_commit' is 'y' and 'use_git_init' is not 'n'
    if use_pre_commit == "y" and use_git_init != "n":
        subprocess.check_call(f"pre-commit install", cwd=PROJECT_ROOT, shell=True)
