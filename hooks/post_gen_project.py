#!/usr/bin/env python
import os
import shutil
import subprocess

PROJECT_ROOT = os.path.realpath(os.path.curdir)


if __name__ == "__main__":

    # Remove test_directory if 'use_test' is not 'y'
    if "{{ cookiecutter.use_test }}" != "y":
        shutil.rmtree(os.path.join(PROJECT_ROOT, "{{cookiecutter.test_directory}}"))

    # Run pre-commit
    PRE_COMMIT_CONFIG = os.path.join(PROJECT_ROOT, ".pre-commit-config.yaml")
    subprocess.check_call(f"pre-commit run --config {PRE_COMMIT_CONFIG} --files ./**/*", cwd=PROJECT_ROOT)