import collections
import json
import logging
import os
import subprocess
import typing

import jinja2.ext  # type: ignore
import requests  # type: ignore

LOGGER = logging.getLogger(__name__)


# TODO: use <https://github.com/haskell/ghcup-metadata.git> to resolve "latest" and "recommended" versions


class HaskellVersionsExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)
        self._versions = None
        environment.filters["resolve_cabal_version"] = self.resolve_cabal_version
        environment.filters["resolve_ghc_version"] = self.resolve_ghc_version

    VERSIONS_JSON_URL = (
        "https://raw.githubusercontent.com/haskell/actions/main/setup/src/versions.json"
    )

    VERSIONS_JSON_FILE = os.path.join(
        os.path.dirname(__file__), os.path.pardir, "versions.json"
    )

    # Cabal versions

    def resolve_cabal_version(self, cabal_version: str) -> str:
        if cabal_version == "latest":
            return self.latest_cabal_version
        elif cabal_version == "installed":
            return self.installed_cabal_version
        elif cabal_version in self.cabal_versions:
            return cabal_version
        else:
            for cabal_version_candidate in self.cabal_versions:
                if cabal_version_candidate.startswith(f"{cabal_version}."):
                    return cabal_version_candidate
            LOGGER.warning(
                f"Unknown Cabal version {cabal_version}, {self.cabal_versions}"
            )
            return cabal_version

    @property
    def installed_cabal_version(self) -> str:
        try:
            return subprocess.getoutput("cabal --numeric-version")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Could not find installed version of Cabal, {e}")

    @property
    def latest_cabal_version(self) -> str:
        if self.cabal_versions:
            return self.cabal_versions[0]
        else:
            return "latest"

    @property
    def cabal_versions(self) -> list[str]:
        return self.versions["cabal"]

    # GHC versions

    def resolve_ghc_version(self, ghc_version: str) -> str:
        if ghc_version == "latest":
            return self.latest_ghc_version
        elif ghc_version == "installed":
            return self.installed_ghc_version
        elif ghc_version in self.ghc_versions:
            return ghc_version
        else:
            for ghc_version_candidate in self.ghc_versions:
                if ghc_version_candidate.startswith(f"{ghc_version}."):
                    return ghc_version_candidate
            LOGGER.warning(f"Unknown GHC version '{ghc_version}', {self.ghc_versions}")
            return ghc_version

    @property
    def installed_ghc_version(self) -> str:
        try:
            return subprocess.getoutput("ghc --numeric-version")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Could not find installed version of GHC, {e}")

    @property
    def latest_ghc_version(self) -> str:
        if self.ghc_versions:
            return self.ghc_versions[0]
        else:
            return "latest"

    @property
    def ghc_versions(self) -> list[str]:
        return self.versions["ghc"]

    @property
    def versions(self) -> dict[str, list[str]]:
        if not hasattr(self, "_versions") or self._versions is None:
            if os.path.exists(self.__class__.VERSIONS_JSON_FILE):
                self._versions = self._get_versions_from_file()
            else:
                self._versions = self._get_versions_from_url()
                with open(self.__class__.VERSIONS_JSON_FILE, "w") as fp:
                    json.dump(self._versions, fp)
        return self._versions

    def _get_versions_from_file(self) -> dict[str, list[str]]:
        if os.path.exists(self.__class__.VERSIONS_JSON_FILE):
            try:
                with open(self.__class__.VERSIONS_JSON_FILE, "rb") as fp:
                    return json.load(fp)
            except (json.JSONDecodeError,) as e:
                LOGGER.warning(f"Could not load versions from file: {e}")
        return typing.cast(
            dict[str, list[str]], collections.defaultdict(default_factory=list)
        )

    def _get_versions_from_url(self) -> dict[str, list[str]]:
        try:
            response = requests.get(self.__class__.VERSIONS_JSON_URL)
            response.raise_for_status()
            return response.json()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.JSONDecodeError,
        ) as e:
            LOGGER.warning(f"Could not load versions from URL: {e}")
            return typing.cast(
                dict[str, list[str]], collections.defaultdict(default_factory=list)
            )
