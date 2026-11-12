import importlib
import os
import pathlib

import dotenv
import dotenv.main
import pytest
from typer.testing import CliRunner

import agentic_radar.cli as cli

runner = CliRunner()

SENTINEL = "AGENTIC_RADAR_ENV_FILE_TEST_SENTINEL"
EXAMPLE_DIR = str(pathlib.Path("examples/langgraph/customer_service").resolve())


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv(SENTINEL, raising=False)
    monkeypatch.delenv("AGENTIC_RADAR_ENV_FILE", raising=False)
    yield
    os.environ.pop(SENTINEL, None)  # load_dotenv writes os.environ directly


def test_import_does_not_search_for_dotenv(monkeypatch):
    """Importing the CLI must not walk the filesystem looking for a .env file."""

    def fail(*args, **kwargs):
        raise AssertionError("find_dotenv() must not be called implicitly")

    monkeypatch.setattr(dotenv.main, "find_dotenv", fail)
    monkeypatch.setattr(dotenv, "find_dotenv", fail)
    importlib.reload(cli)


def test_scan_ignores_dotenv_in_cwd_and_input_dir(tmp_path, monkeypatch):
    repo = tmp_path / "untrusted-repo"
    repo.mkdir()
    (repo / ".env").write_text(f"{SENTINEL}=from-untrusted-repo\n")
    for f in pathlib.Path(EXAMPLE_DIR).glob("*.py"):
        (repo / f.name).write_text(f.read_text())
    monkeypatch.chdir(repo)

    result = runner.invoke(
        cli.app, ["scan", "langgraph", "-i", ".", "-o", str(tmp_path / "r.html")]
    )

    assert result.exit_code == 0, result.stdout
    assert SENTINEL not in os.environ


def test_scan_loads_explicit_env_file(tmp_path):
    env_file = tmp_path / "my.env"
    env_file.write_text(f"{SENTINEL}=explicit\n")

    result = runner.invoke(
        cli.app,
        [
            "scan",
            "langgraph",
            "-i",
            EXAMPLE_DIR,
            "-o",
            str(tmp_path / "r.html"),
            "--env-file",
            str(env_file),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert os.environ.get(SENTINEL) == "explicit"


def test_explicit_env_file_does_not_override_existing_env(tmp_path, monkeypatch):
    monkeypatch.setenv(SENTINEL, "from-shell")
    env_file = tmp_path / "my.env"
    env_file.write_text(f"{SENTINEL}=from-file\n")

    cli.load_env_file(env_file)

    assert os.environ[SENTINEL] == "from-shell"


def test_missing_env_file_is_rejected(tmp_path):
    result = runner.invoke(
        cli.app,
        ["scan", "langgraph", "-i", EXAMPLE_DIR, "--env-file", str(tmp_path / "nope")],
    )
    assert result.exit_code != 0
