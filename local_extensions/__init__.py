import cookiecutter.utils
import re

REGEX_DELIMITER = re.compile(r"[-_.:/](?!\s)+")


@cookiecutter.utils.simple_filter
def to_pascal(
    text: str,
) -> str:
    return "".join(
        [chunk.capitalize() for chunk in REGEX_DELIMITER.sub(" ", text).split()]
    )
