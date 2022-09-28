#!/usr/bin/env python

source_directory = "{{cookiecutter.source_directory}}"
test_directory = "{{cookiecutter.test_directory}}"

if source_directory == test_directory:
    print(
        f"ERROR: 'source_directory' and 'test_directory' cannot be the same directory: {source_directory}"
    )
    exit(1)
