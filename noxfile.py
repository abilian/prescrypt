import nox

PYTHON_VERSIONS = ["3.10", "3.11"]
nox.options.sessions = ["lint", "pytest"]


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    session.install(".")
    session.install("ruff")
    session.run("pip", "check")
    session.run("make", "lint", external=True)


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.install(".")
    session.install("pytest")
    session.run("pip", "check")
    session.run("pytest", "src", "tests")
