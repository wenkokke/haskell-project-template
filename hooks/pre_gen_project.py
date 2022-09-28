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

import re
import requests

VERSIONS_JSON_URL = (
    "https://raw.githubusercontent.com/haskell/actions/main/setup/src/versions.json"
)

REGEX_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)

ghc_version = "{{cookiecutter.ghc_version}}"

cabal_version = "{{cookiecutter.cabal_version}}"

# Verify that ghc_version is a SemVer version number:
if ghc_version != "latest" and not REGEX_SEMVER.match(ghc_version):
    print(f"ERROR: invalid GHC version '{ghc_version}'")
    exit(1)

# Verify that cabal_version is a SemVer version number:
if cabal_version != "latest" and not REGEX_SEMVER.match(cabal_version):
    print(f"ERROR: invalid GHC version '{cabal_version}'")
    exit(1)

# If there are concrete versions, verify them against the list of known versions:
if ghc_version != "latest" or cabal_version != "latest":
    try:
        # Get versions.json from the setup-haskell action:
        response = requests.get(VERSIONS_JSON_URL)
        response.raise_for_status()
        versions = response.json()
        # Verify ghc_version against the list of known GHC versions:
        known_ghc_versions = list(versions["ghc"])
        if ghc_version not in known_ghc_versions:
            print(
                f"ERROR: unknown GHC version '{ghc_version}', not in {known_ghc_versions}'"
            )
            exit(1)
        # Verify cabal_version against the list of known GHC versions:
        known_cabal_versions = list(versions["cabal"])
        if cabal_version not in known_cabal_versions:
            print(
                f"ERROR: unknown cabal version '{cabal_version}', not in {known_cabal_versions}'"
            )
            exit(1)
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
        print(f"WARNING: could not retrieve known GHC and cabal versions")
