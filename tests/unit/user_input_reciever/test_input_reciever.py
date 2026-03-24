from pathlib import Path

import pytest

from app.utils import input_reciever as ir


def _wire_fake_repo(monkeypatch, tmp_path: Path) -> Path:
    fake_repo = tmp_path / "fake_repo"
    fake_module_path = fake_repo / "app" / "utils" / "input_reciever.py"
    fake_module_path.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ir, "__file__", str(fake_module_path))
    return fake_repo


def _write_transcript(fake_repo: Path, ticker: str, filename: str) -> Path:
    transcript_dir = fake_repo / "data" / "Transcripts" / ticker
    transcript_dir.mkdir(parents=True, exist_ok=True)
    path = transcript_dir / filename
    path.write_text("dummy transcript", encoding="utf-8")
    return path


@pytest.fixture
def streamlit_stop_as_exception(monkeypatch):
    errors = []

    def _error(message):
        errors.append(message)

    def _stop():
        raise RuntimeError("STREAMLIT_STOP")

    monkeypatch.setattr(ir.st, "error", _error)
    monkeypatch.setattr(ir.st, "stop", _stop)
    return errors


def test_recieve_input_rejects_non_string_ticker(monkeypatch, tmp_path):
    _wire_fake_repo(monkeypatch, tmp_path)

    with pytest.raises(TypeError):
        ir.recieve_input(None, "Q1", 2016)


@pytest.mark.parametrize("bad_quarter", ["", "Q0", "Q5", "Quarter 1", 1, None])
def test_recieve_input_rejects_invalid_quarter_key(monkeypatch, tmp_path, bad_quarter):
    fake_repo = _wire_fake_repo(monkeypatch, tmp_path)
    _write_transcript(fake_repo, "TEST", "2016-Jan-01-TEST.txt")

    with pytest.raises(KeyError):
        ir.recieve_input("TEST", bad_quarter, 2016)


def test_recieve_input_handles_missing_ticker_directory(monkeypatch, tmp_path, streamlit_stop_as_exception):
    _wire_fake_repo(monkeypatch, tmp_path)

    with pytest.raises(RuntimeError, match="STREAMLIT_STOP"):
        ir.recieve_input("MISSING", "Q1", 2016)

    assert streamlit_stop_as_exception
    assert "Transcript directory not found" in streamlit_stop_as_exception[0]


def test_recieve_input_handles_insufficient_files_for_quarter(monkeypatch, tmp_path, streamlit_stop_as_exception):
    fake_repo = _wire_fake_repo(monkeypatch, tmp_path)
    _write_transcript(fake_repo, "TEST", "2016-Jan-01-TEST.txt")

    with pytest.raises(RuntimeError, match="STREAMLIT_STOP"):
        ir.recieve_input("TEST", "Q4", 2016)

    assert streamlit_stop_as_exception
    assert "Expected at least 4 transcript files" in streamlit_stop_as_exception[0]


def test_recieve_input_handles_year_with_no_matching_files(monkeypatch, tmp_path, streamlit_stop_as_exception):
    fake_repo = _wire_fake_repo(monkeypatch, tmp_path)
    _write_transcript(fake_repo, "TEST", "2016-Jan-01-TEST.txt")
    _write_transcript(fake_repo, "TEST", "2016-Apr-01-TEST.txt")
    _write_transcript(fake_repo, "TEST", "2016-Jul-01-TEST.txt")
    _write_transcript(fake_repo, "TEST", "2016-Oct-01-TEST.txt")

    with pytest.raises(RuntimeError, match="STREAMLIT_STOP"):
        ir.recieve_input("TEST", "Q1", 2020)

    assert streamlit_stop_as_exception
    assert "Expected at least 1 transcript files" in streamlit_stop_as_exception[0]


def test_recieve_input_correctness_case_1():
    ticker = "MSFT"
    quarter = "Q2"
    year = 2018
    expected_filename = "2018-Apr-26-MSFT.txt"

    selected_path = ir.recieve_input(ticker, quarter, year)

    assert selected_path.name == expected_filename


def test_recieve_input_correctness_case_2():
    ticker = "MU"
    quarter = "Q4"
    year = 2016
    expected_filename = "2016-Dec-21-MU.txt"

    selected_path = ir.recieve_input(ticker, quarter, year)

    assert selected_path.name == expected_filename


def test_recieve_input_correctness_case_3():
    ticker = "AMZN"
    quarter = "Q1"
    year = 2019
    expected_filename = "2019-Jan-31-AMZN.txt"

    selected_path = ir.recieve_input(ticker, quarter, year)

    assert selected_path.name == expected_filename


def test_recieve_input_correctness_case_4():
    ticker = "AMD"
    quarter = "Q3"
    year = 2020
    expected_filename = "2020-Jul-28-AMD.txt"

    selected_path = ir.recieve_input(ticker, quarter, year)

    assert selected_path.name == expected_filename

