import re

import jinja2.ext  # type: ignore


class StrCaseExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["to_pascal"] = self.to_pascal

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
