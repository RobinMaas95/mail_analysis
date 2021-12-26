""" Config for 'poetry run nox'."""
# pylint: disable=missing-function-docstring, line-too-long
import nox

nox.options.sessions = (
    "install",  # this is mandatory to ensure, that all needed modules are installed by poetry first
    "black",
    "flake8",
    "pylint",
    "mypy",
    "pytype",
    "safety",
)
locations = "src", "noxfile.py"


@nox.session(python=False)
def install(session):
    session.run("poetry", "install")


@nox.session(python=False)
def black(session):
    args = session.posargs or locations
    session.run("black", "--experimental-string-processing", *args)


@nox.session(python=False)
def flake8(session):
    args = session.posargs or locations
    session.run("flake8", "--docstring-convention=numpy", *args)


@nox.session(python=False)
def pylint(session):
    args = session.posargs or locations
    session.run("pylint", "--output-format=text", *args)


@nox.session(python=False)
def pylint_code_climate(session):
    args = session.posargs or locations
    session.run(
        "pylint",
        "--exit-zero",
        "--output-format=pylint_gitlab.GitlabCodeClimateReporter",
        *args
    )


@nox.session(python=False)
def pylint_pages(session):
    args = session.posargs or locations
    session.run(
        "pylint",
        "--exit-zero",
        "--output-format=pylint_gitlab.GitlabPagesHtmlReporter",
        *args
    )


@nox.session(python=False)
def mypy(session):
    args = session.posargs or locations
    session.run("mypy", *args)


@nox.session(python=False)
def pytype(session):
    session.run("pytype", "--config=pytype.cfg", "src")


@nox.session(python=False)
def safety(session):
    session.run(
        "poetry",
        "export",
        "--dev",
        "--format=requirements.txt",
        "--without-hashes",
        "--output=requirements.txt",
        external=True,
    )
    session.run("safety", "check", "--file=requirements.txt", "--full-report")
