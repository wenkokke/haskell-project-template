#!/usr/bin/env python
import os
import shutil

PROJECT_ROOT = os.path.realpath(os.path.curdir)


if __name__ == "__main__":

    # Remove test_directory if 'use_test' is not 'y'
    if "{{ cookiecutter.use_test }}" != "y":
        shutil.rmtree(os.path.join(PROJECT_ROOT, "{{cookiecutter.test_directory}}"))

    #
