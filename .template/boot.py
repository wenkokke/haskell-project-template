import click
import jinja2
import jinja2.meta
import pathlib
import subprocess
import typing
import yaml

from click.decorators import FC
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from dataclasses_json import config, DataClassJsonMixin
from dataclasses_json.core import Json

template_dir: pathlib.Path = pathlib.Path(__file__).parent
template_files_dir: pathlib.Path = template_dir / "files"


def get_used_variables(
    template_files_dir: pathlib.Path,
) -> Iterator[tuple[pathlib.Path, str]]:
    """
    Get all variables used in the template directory.
    """
    env = jinja2.Environment()
    for template_path in template_files_dir.glob("**/*"):
        if not template_path.samefile(__file__):
            output_path_template = str(template_path.relative_to(template_files_dir))
            output_path_ast = env.parse(source=output_path_template)
            for variable_name in jinja2.meta.find_undeclared_variables(output_path_ast):
                yield (template_path, variable_name)
            if not template_path.is_dir():
                output_template = template_path.read_text()
                output_ast = env.parse(output_template)
                for variable_name in jinja2.meta.find_undeclared_variables(output_ast):
                    yield (template_path, variable_name)


@dataclass
class DefaultSpec(DataClassJsonMixin):
    shell: str

    @staticmethod
    def encoder(
        default_spec: typing.Union[None, str, "DefaultSpec"],
    ) -> Json:
        if default_spec is None or isinstance(default_spec, str):
            return default_spec
        elif isinstance(default_spec, dict):
            return DefaultSpec.to_dict(default_spec)
        else:
            raise TypeError(default_spec)

    @staticmethod
    def decoder(
        kvs: Json,
    ) -> typing.Union[None, str, "DefaultSpec"]:
        if kvs is None or isinstance(kvs, str):
            return kvs
        elif isinstance(kvs, dict):
            return DefaultSpec.from_dict(kvs)
        else:
            raise TypeError(kvs)


@dataclass
class VariableSpec(DataClassJsonMixin):
    name: str
    default: typing.Union[None, str, DefaultSpec] = field(
        default=None,
        metadata=config(decoder=DefaultSpec.decoder, encoder=DefaultSpec.encoder),
    )

    @property
    def has_default(self) -> bool:
        return self.default is not None

    @property
    def prompt(self) -> str:
        return f"Enter {' '.join(self.name.split('_'))}"

    def get_default(self) -> typing.Optional[str]:
        if isinstance(self.default, DefaultSpec):
            self.default = subprocess.getoutput(self.default.shell)
        return self.default

    def option(self) -> Callable[[FC], FC]:
        if self.has_default:
            return click.option(
                f"--{self.name}", prompt=self.prompt, default=self.get_default()
            )
        else:
            return click.option(f"--{self.name}", prompt=self.prompt)


@dataclass
class ProjectSpec:
    variables: list[VariableSpec] = field(default_factory=list)

    def load(self, path: pathlib.Path):
        contents = yaml.safe_load(path.read_text())
        for variable_dict in contents["variables"]:
            variable_spec = VariableSpec.from_dict(variable_dict)
            self.variables.append(variable_spec)

    def test(self, template_files_dir: pathlib.Path):
        """
        Test whether all used variables have a spec.
        """
        for template_path, variable_name in get_used_variables(template_files_dir):
            if not any(variable_name == variable.name for variable in self.variables):
                print(f"Undefined variable '{variable_name}' in '{template_path}'")

    def command(self) -> Callable[[FC], FC]:
        """
        Create a click decorator for a given variable spec.
        """
        decorator: Callable[[FC], FC] = lambda fc: fc
        for variable_spec in self.variables:
            decorator = lambda fc: variable_spec.option()(decorator(fc))
        return click.command()(decorator)


project_spec = ProjectSpec()
project_spec.load(template_dir / "variables.yaml")
project_spec.test(template_files_dir)


# @click.command()
# @click.help_option()
# def cli(**kwargs) -> None:
#     confirmation_dialog = "\n".join(
#         [
#             "Initialize project with the following options:",
#             "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
#             "Ok?",
#         ]
#     )
#     click.confirm(text=confirmation_dialog)
#     output_dir = pathlib.Path(__file__).parent.parent
#     template_dir = pathlib.Path(__file__).parent / ".template"
#     env = jinja2.Environment()
#     for template_path in template_dir.glob("**/*"):
#         output_path_template: str = str(
#             template_path.relative_to(template_dir)
#         ).replace(".jinja2", "")
#         output_path = env.from_string(source=output_path_template).render(**kwargs)
#         print(f"{output_path_template} -> {output_path}")
#         output_path = project_dir / output_path
#         if template_path.is_dir():
#             output_path.mkdir(parents=True, exist_ok=True)
#         else:
#             output_path_contents = env.get_template(output_path_template).render(**kwargs)
#             output_path.write_text(output_path_contents)


# if __name__ == "__main__":
#     cli()
