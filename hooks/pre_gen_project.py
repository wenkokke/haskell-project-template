#!/usr/bin/env python

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

import os
import sys

TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), os.path.pardir)

sys.path.append(TEMPLATE_ROOT)

import local_extensions

versions = local_extensions.HaskellVersions()

ghc_version = "{{cookiecutter.ghc_version}}"

cabal_version = "{{cookiecutter.cabal_version}}"

# Verify that ghc_version is a SemVer version number:
if ghc_version != "latest" and not versions.is_semver(ghc_version):
    print(f"ERROR: invalid GHC version '{ghc_version}'")
    exit(1)

# Verify that cabal_version is a SemVer version number:
if cabal_version != "latest" and not versions.is_semver(cabal_version):
    print(f"ERROR: invalid GHC version '{cabal_version}'")
    exit(1)


# Verify ghc_version against the list of known GHC versions:
if ghc_version != "latest" and versions.ghc_versions and ghc_version not in versions.ghc_versions:
    print(
        f"ERROR: unknown GHC version '{ghc_version}', not in {versions.ghc_versions}'"
    )
    exit(1)

# Verify cabal_version against the list of known cabal versions:
if cabal_version != "latest" and versions.cabal_versions and cabal_version not in versions.cabal_versions:
    print(
        f"ERROR: unknown cabal version '{cabal_version}', not in {versions.cabal_versions}'"
    )
    exit(1)
