#!/usr/bin/env python
import re

################################################################################
# Check that source_directory and test_directory are distinct
################################################################################

source_directory = "{{cookiecutter.source_directory}}"
test_directory = "{{cookiecutter.test_directory}}"

if source_directory == test_directory:
    print(
        f"ERROR: 'source_directory' and 'test_directory' cannot be the same directory: {source_directory}"
    )
    exit(1)

################################################################################
# Check that ghc_version and cabal_version are valid
################################################################################

ghc_version = "{{cookiecutter.ghc_version}}"

if ghc_version != "latest" and not re.match(r"\d+\.\d+\.\d+", ghc_version):
    print(f"ERROR: invalid GHC version '{ghc_version}'")
    exit(2)

cabal_version = "{{cookiecutter.cabal_version}}"

if cabal_version != "latest" and not re.match(r"(\d+\.\d+)(\.\d+)?", cabal_version):
    print(f"ERROR: invalid GHC version '{cabal_version}'")
    exit(2)
