"""Integration tests for paper_reader CLI."""

from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from paper_reader.main import cli


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Use temporary directory for data."""
    data_dir = tmp_path / "data"
    monkeypatch.setenv("HOME", str(tmp_path))
    return data_dir


def test_cli_help(runner):
    """Test CLI help."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Paper Reader" in result.output


def test_init_command(runner, temp_data_dir):
    """Test init command."""
    result = runner.invoke(cli, ["init"], input="deep learning\nattention\ncs.LG\n")

    assert result.exit_code == 0
    assert "Interests saved" in result.output


def test_list_empty(runner, temp_data_dir):
    """Test list command with no papers."""
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "No papers" in result.output


@patch("paper_reader.main.discoverer")
def test_discover_command(mock_discoverer, runner, temp_data_dir):
    """Test discover command."""
    # Setup interests
    runner.invoke(cli, ["init"], input="deep learning\nattention\ncs.LG\n")

    # Mock discovery
    mock_candidate = Mock()
    mock_candidate.id = "arxiv:2301.12345"
    mock_candidate.title = "Test Paper"
    mock_candidate.authors = ["Author One"]
    mock_candidate.published_date = "2025-10-31T00:00:00"
    mock_candidate.url = "https://arxiv.org/abs/2301.12345"

    mock_discoverer.discover.return_value = [mock_candidate]

    result = runner.invoke(cli, ["discover"])

    assert result.exit_code == 0
    assert "Test Paper" in result.output


def test_search_not_found(runner, temp_data_dir):
    """Test search with no results."""
    result = runner.invoke(cli, ["search", "nonexistent"])

    assert result.exit_code == 0
    assert "No papers found" in result.output


def test_show_not_found(runner, temp_data_dir):
    """Test show with non-existent paper."""
    result = runner.invoke(cli, ["show", "arxiv:9999.99999"])

    assert result.exit_code == 0
    assert "not found" in result.output


def test_update_status_not_found(runner, temp_data_dir):
    """Test update-status with non-existent paper."""
    result = runner.invoke(cli, ["update-status", "arxiv:9999.99999", "read"])

    assert result.exit_code == 0
    assert "not found" in result.output


def test_delete_not_found(runner, temp_data_dir):
    """Test delete with non-existent paper."""
    result = runner.invoke(cli, ["delete", "arxiv:9999.99999"], input="y\n")

    assert result.exit_code == 0
    assert "not found" in result.output
