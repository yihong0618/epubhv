"""--punctuation must reach EPUBHV for single files and directories alike.

The directory branch always forwarded it, but the single-file branch
dropped it, so e.g. ``epubhv book.epub --punctuation t2s`` silently used
the ``auto`` default.

fugashi instantiates its MeCab Tagger at import time inside
epubhv.yomituki, which needs a dictionary file; stub it so this CLI
plumbing can be tested without one (EPUBHV itself is mocked below, so no
tokenizer ever runs).
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

_fugashi = types.ModuleType("fugashi")


class _Tagger:
    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def __call__(self, sentence: str) -> list:
        return []


_fugashi.Tagger = _Tagger
sys.modules["fugashi"] = _fugashi

from epubhv import cli as cli_mod  # noqa: E402


def _run(monkeypatch: pytest.MonkeyPatch, *argv: str):
    monkeypatch.setattr("sys.argv", ["epubhv", *argv])
    with patch.object(cli_mod, "EPUBHV") as mock:
        cli_mod.main()
    return mock


def test_single_file_forwards_punctuation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    book = tmp_path / "book.epub"
    book.touch()
    mock = _run(monkeypatch, str(book), "--punctuation", "t2s")
    mock.assert_called_once()
    assert mock.call_args.kwargs["convert_punctuation"] == "t2s"


def test_single_file_defaults_to_auto(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    book = tmp_path / "book.epub"
    book.touch()
    mock = _run(monkeypatch, str(book))
    assert mock.call_args.kwargs["convert_punctuation"] == "auto"


def test_directory_forwards_punctuation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "a.epub").touch()
    mock = _run(monkeypatch, str(tmp_path), "--punctuation", "none")
    assert mock.call_count == 1
    assert mock.call_args.kwargs["convert_punctuation"] == "none"
