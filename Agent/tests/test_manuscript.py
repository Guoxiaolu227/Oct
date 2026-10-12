from pathlib import Path

import pytest

from r3_agent.errors import InputError, InputTooLargeError
from r3_agent.manuscript import Manuscript


def test_mmd_loading_normalizes_newlines_and_numbers_lines(tmp_path: Path) -> None:
    path = tmp_path / "paper.mmd"
    path.write_bytes(b"# Title\r\nFirst line\r\nSecond line")
    manuscript = Manuscript.load(path, allowed_extensions=[".mmd"], max_characters=1000)

    assert manuscript.text == "# Title\nFirst line\nSecond line"
    assert manuscript.numbered_text().splitlines()[1] == "0002 | First line"
    quote = manuscript.verify_quote("First line", 2, 2)
    assert manuscript.text[quote.char_start:quote.char_end] == "First line"


def test_quote_must_match_the_stated_lines(tmp_path: Path) -> None:
    path = tmp_path / "paper.mmd"
    path.write_text("# Title\nExact evidence\nOther", encoding="utf-8")
    manuscript = Manuscript.load(path, allowed_extensions=[".mmd"], max_characters=1000)

    with pytest.raises(ValueError, match="does not occur exactly"):
        manuscript.verify_quote("Exact evidence", 3, 3)


def test_oversized_mmd_fails_without_truncation(tmp_path: Path) -> None:
    path = tmp_path / "paper.mmd"
    path.write_text("x" * 101, encoding="utf-8")

    with pytest.raises(InputTooLargeError, match="input_too_large"):
        Manuscript.load(path, allowed_extensions=[".mmd"], max_characters=100)


def test_non_mmd_input_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "paper.pdf"
    path.write_bytes(b"not a pdf parser")

    with pytest.raises(InputError, match="Only .mmd"):
        Manuscript.load(path, allowed_extensions=[".mmd"], max_characters=1000)
