from pathlib import Path
from tempfile import NamedTemporaryFile

import nox

_TRAINING_ONLY_PACKAGES = ("tinker==", "tinker-cookbook==")


def _install_dev_deps_without_training_extras(session: nox.Session) -> None:
    """Install lockfile deps while skipping training-only extras.

    `test-pydantic-v1` runs on Python 3.9 to validate base SDK compatibility.
    Training extras (`tinker`, `tinker-cookbook`) currently require newer
    Python versions, so we exclude only those packages from the shared dev
    lockfile for this session.
    """
    lockfile_lines = Path("requirements-dev.lock").read_text(encoding="utf-8").splitlines()
    filtered_lines = [
        line for line in lockfile_lines if not line.strip().startswith(_TRAINING_ONLY_PACKAGES)
    ]

    with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False) as temp_requirements:
        temp_requirements.write("\n".join(filtered_lines) + "\n")
        temp_requirements_path = temp_requirements.name

    session.install("-r", temp_requirements_path)


@nox.session(reuse_venv=True, name="test-pydantic-v1")
def test_pydantic_v1(session: nox.Session) -> None:
    _install_dev_deps_without_training_extras(session)
    session.install("pydantic<2")

    session.run("pytest", "--showlocals", "--ignore=tests/functional", *session.posargs)
