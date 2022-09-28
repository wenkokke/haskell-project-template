#!/usr/bin/env python

import subprocess
import sys

################################################################################
# Check that source_directory and test_directory are distinct
################################################################################

source_directory = "{{cookiecutter.source_directory}}"
test_directory = "{{cookiecutter.test_directory}}"

if source_directory == test_directory:
    sys.stderr.writelines(
        [
            f"ERROR: 'source_directory' and 'test_directory' cannot be the same directory: {source_directory}\n"
        ]
    )
    exit(1)

################################################################################
# Print GHC and cabal versions
################################################################################

ghc_version = "{{cookiecutter.ghc_version}}"

sys.stderr.writelines([f"Using GHC version {ghc_version}"])

cabal_version = "{{cookiecutter.cabal_version}}"

sys.stderr.writelines([f"Using Cabal version {ghc_version}"])

################################################################################
# Check that fullname and email match git config
################################################################################

try:
    fullname = "{{cookiecutter.fullname}}"
    git_fullname = subprocess.getoutput("git config --get user.name")
    if fullname != git_fullname:
        sys.stderr.writelines(
            [f"'{fullname}' does not match git config: '{git_fullname}'"]
        )
except subprocess.CalledProcessError as e:
    sys.stderr.writelines([f"Could not check git config", str(e)])

try:
    email = "{{cookiecutter.email}}"
    git_email = subprocess.getoutput("git config --get user.email")
    if email != git_email:
        sys.stderr.writelines([f"'{email}' does not match git config: '{git_email}'\n"])
except subprocess.CalledProcessError as e:
    sys.stderr.writelines([f"Could not check git config", str(e)])
