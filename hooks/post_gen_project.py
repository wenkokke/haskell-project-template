#!/usr/bin/env python
import os
import shutil
import subprocess

PROJECT_ROOT = os.path.realpath(os.path.curdir)


if __name__ == "__main__":

    # Remove test_directory if 'use_test' is not 'y':
    if "{{cookiecutter.use_test}}" != "y":
        shutil.rmtree(os.path.join(PROJECT_ROOT, "{{cookiecutter.test_directory}}"))

    # Initialize a git repository with a github remote if 'use_git' is 'github':
    if "{{cookiecutter.use_git_init}}" == "github":
        github_remote_url = "{{cookiecutter.__github_remote_url}}"
        subprocess.check_call(f"git init", cwd=PROJECT_ROOT, shell=True)
        subprocess.check_call(
            f"git remote add origin {github_remote_url}", cwd=PROJECT_ROOT, shell=True
        )

    # Run pre-commit if 'use_pre_commit' is 'y':
    if "{{cookiecutter.use_pre_commit}}" == "y":
        subprocess.check_call(
            f"pre-commit run --files ./**/*", cwd=PROJECT_ROOT, shell=True
        )
