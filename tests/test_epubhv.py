import os
from pathlib import Path
from shutil import rmtree

import opencc
from typing import Dict

import pytest
from epubhv import EPUBHV, Punctuation, _make_epub_files_dict, list_all_epub_in_dir


@pytest.fixture
def epub() -> EPUBHV:
    return EPUBHV(Path("tests/test_epub/animal_farm.epub"))


def test_find_epub_books() -> None:
    assert list_all_epub_in_dir(Path("tests/test_epub")) == {
        Path("tests/test_epub/animal_farm.epub"),
        Path("tests/test_epub/Liber_Esther.epub"),
        Path("tests/test_epub/books/lemo.epub"),
        Path("tests/test_epub/sanguo.epub"),
    }


def test_extract_epub_path(epub: EPUBHV) -> None:
    epub.extract_one_epub_to_dir()
    assert Path(".epub_temp_dir/animal_farm").exists()
    rmtree(".epub_temp_dir/animal_farm")


def test_make_files_dict(epub: EPUBHV) -> None:
    epub.extract_one_epub_to_dir()
    d: Dict = dict(_make_epub_files_dict(".epub_temp_dir/animal_farm"))
    assert sorted(
        [".html", ".css", ".xhtml", "", ".opf", ".ncx", ".jpg", ".xml"]
    ) == sorted(list(d.keys()))
    assert 19 == len(d.get(".html", 0))
    rmtree(".epub_temp_dir/animal_farm")


def test_change_epub_to_vertical():
    epub_file = Path("animal_farm-v-original.epub")
    epub_file.unlink(True)
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b.run()
    assert b.opf_file == Path(".epub_temp_dir/animal_farm/content.opf")
    epub_file.unlink(True)


def test_find_epub_css_files():
    lemo_output = Path("lemo-h-original.epub")
    lemo_output.unlink(True)
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b._make_epub_values()
    assert b.has_css_file is False
    b.run()
    os.remove("animal_farm-v-original.epub")
    f: EPUBHV = EPUBHV("tests/test_epub/books/lemo.epub")
    f.run("to_horizontal")
    assert lemo_output.exists()
    lemo_output.unlink(True)


def test_change_epub_covert() -> None:
    if os.path.exists("sanguo-v-s2t-v-original.epub"):
        os.remove("sanguo-v-s2t-v-original.epub")
    if os.path.exists("sanguo-v-s2t.epub"):
        os.remove("sanguo-v-s2t.epub")
    f: EPUBHV = EPUBHV("tests/test_epub/sanguo.epub", "s2t")
    f.run("to_vertical")
    assert os.path.exists("sanguo-v-s2t.epub") is True
    q: EPUBHV = EPUBHV("sanguo-v-s2t.epub")
    q.extract_one_epub_to_dir()
    q._make_epub_values()
    has_t_count: int = 0
    for html_file in (
        q.files_dict.get(".html", [])
        + q.files_dict.get(".xhtml", [])
        + q.files_dict.get(".htm", [])
    ):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            r: str = f.read()
            if r.find("滾滾長江東逝水") > 0:
                has_t_count += 1
    assert has_t_count > 0
    q.run("to_vertical")
    os.remove("sanguo-v-s2t.epub")
    os.remove("sanguo-v-s2t-v-original.epub")


def test_punctuation():
    punctuation = Punctuation()

    res = punctuation.convert(
        "﹃我最赞成罗素先生的一句话：﹁须知参差多态，乃是幸福的本源。﹂大多数的参差多态都是敏于思索的人创造出来的。﹄",
        True,
        "hans",
        "hant",
    )
    res = opencc.OpenCC("s2t").convert(res)
    assert res == """「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」"""

    res = punctuation.convert(
        "﹁我最贊成羅素先生的一句話：﹃須知參差多態，乃是幸福的本源。﹄大多數的參差多態都是敏於思索的人創造出來的。﹂",
        True,
        "hant",
        "hans",
    )
    res = opencc.OpenCC("t2s").convert(res)
    assert res == """“我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”"""

    res = punctuation.convert(
        "“我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”",
        False,
        "hans",
        "hant",
    )
    res = opencc.OpenCC("s2t").convert(res)
    assert res == """「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」"""

    res = punctuation.convert(
        "「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」",
        False,
        "hant",
        "hans",
    )
    res = opencc.OpenCC("t2s").convert(res)
    assert res == """『我最赞成罗素先生的一句话：「须知参差多态，乃是幸福的本源。」大多数的参差多态都是敏于思索的人创造出来的。』"""
