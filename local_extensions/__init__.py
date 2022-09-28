from jinja2.ext import Extension
import re


class HaskellExtension(Extension):
    REGEX_DELIMITER = re.compile(r"[-_.:/](?!\s)+")

    def __init__(self, environment):
        super(HaskellExtension, self).__init__(environment)
        environment.filters["to_pascal"] = HaskellExtension.to_pascal

    @staticmethod
    def to_pascal(
        text: str,
    ) -> str:
        return "".join(
            [
                chunk.capitalize()
                for chunk in HaskellExtension.REGEX_DELIMITER.sub(" ", text).split()
            ]
        )
