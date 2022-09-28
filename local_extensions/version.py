import re

import jinja2.ext  # type: ignore


class VersionExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["version_pattern"] = self.version_pattern
        environment.filters["major_minor"] = self.major_minor
        environment.filters["major_minor_patch"] = self.major_minor_patch

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
