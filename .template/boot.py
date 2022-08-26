import os
import click
import jinja2
import jinja2.meta
import pathlib
import platform
import subprocess
import typing
import yaml

template_dir: pathlib.Path = pathlib.Path(__file__).parent
template_files_dir: pathlib.Path = template_dir / "files"


def get_variables(
    template_dir: pathlib.Path, env: typing.Optional[jinja2.Environment] = None
) -> set[str]:
    env = env or jinja2.Environment()
    variables: set[str] = set()
    for template_path in template_dir.glob("**/*"):
        if template_path.is_dir():
            pass
        elif not template_path.samefile(__file__):
            template_path_ast = env.parse(
                source=str(template_path.relative_to(template_dir))
            )
            variables.update(jinja2.meta.find_undeclared_variables(template_path_ast))
            template = template_path.read_text()
            template_ast = env.parse(template)
            variables.update(jinja2.meta.find_undeclared_variables(template_ast))
    return variables


print(get_variables(template_files_dir))
print(yaml.safe_load((template_dir/"variables.yaml").read_text()))

# @click.command()
# @click.option("--project", prompt="Project name", help="The project name.")
# @click.option("--author-name", default=defaults["author_name"])
# @click.option("--author-email", default=defaults["author_email"])
# @click.option("--version", default=defaults["version"])
# @click.option("--version-pattern", default=defaults["version_pattern"])
# @click.option("--src-dir", default=defaults["src_dir"])
# @click.option("--test-dir", default=defaults["test_dir"])
# @click.option("--license", default=defaults["license"])
# @click.option("--ghc-version", default=defaults["ghc_version"])
# @click.option("--python-version", default=defaults["python_version"])
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
