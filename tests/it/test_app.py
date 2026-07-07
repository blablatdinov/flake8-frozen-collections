# flake8: noqa: S
# Not a production code

import os
import subprocess
from collections.abc import Generator
from pathlib import Path
from shutil import copy2

import pytest
from _pytest.legacypath import TempdirFactory


@pytest.fixture(scope="module")
def current_dir() -> Path:
    return Path().absolute()


@pytest.fixture(scope="module")
def _test_dir(
    tmpdir_factory: TempdirFactory, current_dir: str
) -> Generator[None, None, None]:
    tmp_path = tmpdir_factory.mktemp("test")
    copy2(Path("tests/fixtures/file.py.txt"), tmp_path / "file.py")
    os.chdir(tmp_path)
    subprocess.run(["python", "-m", "venv", "venv"], check=True)
    subprocess.run(["venv/bin/pip", "install", "pip", "-U"], check=True)
    subprocess.run(["venv/bin/pip", "install", str(current_dir)], check=True)
    yield
    os.chdir(current_dir)


def _run_flake8() -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["venv/bin/flake8", "file.py", "--max-line-length=120"],
        stdout=subprocess.PIPE,
        check=False,
    )


@pytest.mark.usefixtures("_test_dir")
@pytest.mark.parametrize(
    "version",
    [
        ("flake8==7.0.0",),
        ("flake8", "-U"),
    ],
)
def test_dependency_versions(version: tuple[str]) -> None:
    """Test script with different dependency versions."""
    subprocess.run(["venv/bin/pip", "install", *version], check=True)
    got = _run_flake8()

    assert got.returncode == 1
    assert b"FCS100 use frozendict instead of dict" in got.stdout
    assert b"FCS200 use frozenset instead of set" in got.stdout


@pytest.mark.usefixtures("_test_dir")
def test() -> None:
    """Test script."""
    got = _run_flake8()

    assert got.returncode == 1
    assert got.stdout.count(b"FCS100") == 2
    assert got.stdout.count(b"FCS200") == 2
