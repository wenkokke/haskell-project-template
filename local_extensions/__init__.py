import collections
import json
import logging
import os
import re
import requests  # type: ignore
import subprocess
import typing

LOGGER = logging.getLogger(__name__)

# TODO: use <https://github.com/haskell/ghcup-metadata.git> to resolve "latest" and "recommended" versions


class BumpverExtension:

    REGEX_SEMVER = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    )

    def version_pattern(self, version_style: str) -> str:
        if version_style == "SemVer":
            return "MAJOR.MINOR.PATCH"
        elif version_style == "ComVer":
            return "MAJOR.MINOR"
        elif version_style == "CalVer":
            return "YYYY.MM[.INC0]"
        raise ValueError(f"Unknown version style {version_style}")

    def is_semver(self, version: str) -> bool:
        return bool(self.__class__.REGEX_SEMVER.match(version))

    def major_minor(self, version: str) -> str:
        return ".".join(version.split(".")[:2])

    def major_minor_patch(self, version: str) -> str:
        return ".".join(version.split(".")[:3])


class HaskellVersionExtension:

    VERSIONS_JSON_URL = (
        "https://raw.githubusercontent.com/haskell/actions/main/setup/src/versions.json"
    )

    VERSIONS_JSON_FILE = os.path.join(
        os.path.dirname(__file__), os.path.pardir, "versions.json"
    )

    def __init__(self):
        self._versions = None

    # Cabal versions

    def resolve_cabal_version(self, cabal_version: str) -> str:
        if cabal_version == "latest":
            return self.latest_cabal_version
        elif cabal_version == "installed":
            return self.installed_cabal_version
        elif cabal_version in self.cabal_versions:
            return cabal_version
        elif self.is_semver(cabal_version):
            for cabal_version_candidate in self.cabal_versions:
                if cabal_version_candidate.startswith(f"{cabal_version}."):
                    return cabal_version_candidate
        LOGGER.warning(f"Unknown Cabal version {cabal_version}, {self.cabal_versions}")
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
        elif self.is_semver(ghc_version):
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
        if not hasattr(self, "_versions"):
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


class StrCaseExtension:

    REGEX_DELIMITER = re.compile(r"[-_.:/](?!\s)+")

    def to_pascal(
        self,
        text: str,
    ) -> str:
        return "".join(
            [
                chunk.capitalize()
                for chunk in self.REGEX_DELIMITER.sub(" ", text).split()
            ]
        )


try:
    import jinja2.ext  # type: ignore

    class LocalExtensions(
        jinja2.ext.Extension,
        BumpverExtension,
        HaskellVersionExtension,
        StrCaseExtension,
    ):
        def __init__(self, environment):
            super(jinja2.ext.Extension, self).__init__(environment)
            # BumpverExtension
            environment.filters["version_pattern"] = self.version_pattern
            environment.filters["major_minor"] = self.major_minor
            environment.filters["major_minor_patch"] = self.major_minor_patch
            # HaskellVersionExtension
            environment.filters["resolve_cabal_version"] = self.resolve_cabal_version
            environment.filters["resolve_ghc_version"] = self.resolve_ghc_version
            # StrCaseExtension
            environment.filters["to_pascal"] = self.to_pascal

except ModuleNotFoundError as e:
    pass
