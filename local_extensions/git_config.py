import subprocess
import typing

import jinja2.ext  # type: ignore


class GitConfigExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["resolve_fullname"] = self.resolve_fullname
        environment.filters["resolve_email"] = self.resolve_email

    def resolve_fullname(self, fullname: typing.Optional[str]) -> str:
        if fullname is None:
            try:
                return subprocess.getoutput("git config --get user.name")
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Could not resolve fullname, {e}")
        return fullname

    def resolve_email(self, email: typing.Optional[str]) -> str:
        if email is None:
            try:
                return subprocess.getoutput("git config --get user.email")
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Could not resolve email, {e}")
        return email
