import click
import jinja2
import pathlib
import platform
import subprocess
import typing


def default_author_name() -> typing.Optional[str]:
    try:
        return subprocess.getoutput("git config --get user.name")
    except subprocess.CalledProcessError:
        return None


def default_author_email() -> typing.Optional[str]:
    try:
        return subprocess.getoutput("git config --get user.email")
    except subprocess.CalledProcessError:
        return None


def default_ghc_version():
    try:
        return subprocess.getoutput("ghc --numeric-version")
    except subprocess.CalledProcessError:
        return None


defaults: dict[str, typing.Optional[str]] = {
    "author_name": default_author_name(),
    "author_email": default_author_email(),
    "version": "0.0.1",
    "version_pattern": "MAJOR.MINOR.PATCH",
    "src_dir": "src",
    "test_dir": "test",
    "license": "AllRightsReserved",
    "ghc_version": default_ghc_version(),
    "python_version": platform.python_version(),
}


@click.command()
@click.option("--project", prompt="Project name", help="The project name.")
@click.option("--author-name", default=defaults["author_name"])
@click.option("--author-email", default=defaults["author_email"])
@click.option("--version", default=defaults["version"])
@click.option("--version-pattern", default=defaults["version_pattern"])
@click.option("--src-dir", default=defaults["src_dir"])
@click.option("--test-dir", default=defaults["test_dir"])
@click.option("--license", default=defaults["license"])
@click.option("--ghc-version", default=defaults["ghc_version"])
@click.option("--python-version", default=defaults["python_version"])
@click.help_option()
def cli(**kwargs) -> None:
    confirmation_dialog = "\n".join(
        [
            "Initialize project with the following options:",
            "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
            "Ok?",
        ]
    )
    click.confirm(text=confirmation_dialog)
    template_dir = pathlib.Path(__file__).parent/"template"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
    for template_file in template_dir.glob("**/*"):
        template_file = template_file.relative_to(template_dir)
        output_file = pathlib.Path(env.from_string(source=str(template_file)).render(**kwargs))
        if template_file.is_dir():
            print(f"Create directory {output_file}")
            output_file.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Create file {output_file}")
            output_file.write_text(env.get_template(str(template_file)).render(**kwargs))


if __name__ == "__main__":
    cli()
