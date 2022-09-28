import collections
import json
import logging
import os
import re
import requests

LOGGER = logging.getLogger(__name__)


class HaskellVersions:
    def __init__(self):
        self._versions = None

    REGEX_SEMVER = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    )

    def is_semver(self, version: str) -> bool:
        return bool(self.__class__.REGEX_SEMVER.match(version))

    VERSIONS_JSON_URL = (
        "https://raw.githubusercontent.com/haskell/actions/main/setup/src/versions.json"
    )

    VERSIONS_JSON_FILE = os.path.join(
        os.path.dirname(__file__), os.path.pardir, "versions.json"
    )

    def resolve_latest_cabal_version(self, cabal_version: str) -> str:
        if cabal_version == "latest":
            return self.latest_cabal_version
        else:
            return cabal_version

    @property
    def latest_cabal_version(self):
        if self.cabal_versions:
            return self.cabal_versions[0]
        else:
            return "latest"

    @property
    def cabal_versions(self):
        return self.versions["cabal"]

    def resolve_latest_ghc_version(self, ghc_version: str) -> str:
        if ghc_version == "latest":
            return self.latest_ghc_version
        else:
            return ghc_version

    @property
    def latest_ghc_version(self):
        if self.ghc_versions:
            return self.ghc_versions[0]
        else:
            return "latest"

    @property
    def ghc_versions(self):
        return self.versions["ghc"]

    @property
    def versions(self):
        if self._versions is None:
            if os.path.exists(self.__class__.VERSIONS_JSON_FILE):
                self._versions = self._get_versions_from_file()
            else:
                self._versions = self._get_versions_from_url()
                with open(self.__class__.VERSIONS_JSON_FILE, "wb") as fp:
                    json.dump(self._versions, fp)
        return self._versions

    def _get_versions_from_file(self):
        if os.path.exists(self.__class__.VERSIONS_JSON_FILE):
            try:
                with open(self.__class__.VERSIONS_JSON_FILE, "rb") as fp:
                    return json.load(fp)
            except (json.JSONDecodeError,) as e:
                LOGGER.warning(f"Could not load versions from file: {e}")
        return collections.defaultdict(default_factory=list)

    def _get_versions_from_url(self):
        try:
            response = requests.get(self.__class__.VERSIONS_JSON_URL)
            response.raise_for_status()
            return response.json()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.JSONDecodeError,
        ) as e:
            LOGGER.warning(f"Could not load versions from URL: {e}")
            return collections.defaultdict(default_factory=list)


class HaskellStrCase:

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
    import jinja2.ext

    class HaskellExtension(jinja2.ext.Extension, HaskellVersions, HaskellStrCase):
        def __init__(self, environment):
            super(HaskellExtension, self).__init__(environment)
            super(HaskellVersions, self).__init__()
            super(HaskellStrCase, self).__init__()
            environment.filters["to_pascal"] = self.to_pascal
            environment.filters[
                "resolve_latest_cabal_version"
            ] = self.resolve_latest_cabal_version
            environment.filters[
                "resolve_latest_ghc_version"
            ] = self.resolve_latest_ghc_version

except ModuleNotFoundError as e:
    pass
