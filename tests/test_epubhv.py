from pathlib import Path
from shutil import rmtree
from typing import Dict, List

import opencc
import pytest

from epubhv.epubhv import (
    EPUBHV,
    Punctuation,
    list_all_epub_in_dir,
    make_epub_files_dict,
)

TEST_DIR = Path(__file__).with_name("test_epub")


@pytest.fixture
def epub() -> EPUBHV:
    return EPUBHV(file_path=TEST_DIR / "animal_farm.epub")


def test_find_epub_books() -> None:
    assert list_all_epub_in_dir(TEST_DIR) == {
        TEST_DIR / "animal_farm.epub",
        TEST_DIR / "books/animal.epub",
        TEST_DIR / "Liber_Esther.epub",
        TEST_DIR / "books/lemo.epub",
        TEST_DIR / "sanguo.epub",
    }


def test_extract_epub_path(epub: EPUBHV) -> None:
    epub.extract_one_epub_to_dir()
    assert Path(".epub_temp_dir/animal_farm").exists()
    rmtree(".epub_temp_dir/animal_farm")


def test_make_files_dict(epub: EPUBHV) -> None:
    epub.extract_one_epub_to_dir()
    d: Dict[str, List[Path]] = dict(
        make_epub_files_dict(dir_path=Path(".epub_temp_dir/animal_farm"))
    )
    assert sorted(
        [".html", ".css", ".xhtml", "", ".opf", ".ncx", ".jpg", ".xml"]
    ) == sorted(list(d.keys()))
    assert 19 == len(d.get(".html", []))
    rmtree(".epub_temp_dir/animal_farm")


def test_change_epub_to_vertical(epub: EPUBHV, tmp_path: Path) -> None:
    epub.run(dest=tmp_path)
    assert epub.opf_file == Path(".epub_temp_dir/animal_farm/content.opf")
    assert tmp_path.joinpath("animal_farm-v-original.epub").exists()


def test_find_epub_css_files(tmp_path: Path) -> None:
    lemo_output = tmp_path / "lemo-h-original.epub"
    b = EPUBHV(TEST_DIR / "animal_farm.epub")
    b.make_epub_values()
    assert b.has_css_file is False
    b.run(dest=tmp_path)

    f = EPUBHV(TEST_DIR / "books/lemo.epub")
    f.run("to_horizontal", dest=tmp_path)
    assert lemo_output.exists()


def test_change_epub_covert(tmp_path: Path) -> None:
    f = EPUBHV(TEST_DIR / "sanguo.epub", "s2t")
    f.run("to_vertical", dest=tmp_path)
    assert tmp_path.joinpath("sanguo-v-s2t.epub").exists()
    q = EPUBHV(tmp_path.joinpath("sanguo-v-s2t.epub"))
    q.extract_one_epub_to_dir()
    q.make_epub_values()
    has_t_count: int = 0
    for html_file in (
        q.files_dict.get(".html", [])
        + q.files_dict.get(".xhtml", [])
        + q.files_dict.get(".htm", [])
    ):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as file:
            r: str = file.read()
            if r.find("滾滾長江東逝水") > 0:
                has_t_count += 1
    assert has_t_count > 0
    q.run("to_vertical", dest=tmp_path)


def test_ruby(tmp_path: Path) -> None:
    lemo_output = tmp_path / "lemo-h-original-ruby.epub"
    f = EPUBHV(TEST_DIR / "books/lemo.epub", need_ruby=True)
    f.run("to_horizontal", dest=tmp_path)
    assert f.ruby_language == "ja"
    assert lemo_output.exists()


def test_cantonese(tmp_path: Path) -> None:
    animal_output = tmp_path / "animal-h-original-ruby.epub"
    f = EPUBHV(TEST_DIR / "books/animal.epub", need_ruby=True, need_cantonese=True)
    f.run("to_horizontal", dest=tmp_path)
    assert f.ruby_language == "cantonese"
    assert animal_output.exists()


def test_punctuation():
    punctuation = Punctuation()

    res: str = punctuation.convert(
        "﹃我最赞成罗素先生的一句话：﹁须知参差多态，乃是幸福的本源。﹂大多数的参差多态都是敏于思索的人创造出来的。﹄",
        True,
        "hans",
        "hant",
    )
    res = opencc.OpenCC("s2t").convert(res)  # type: ignore
    assert res == """「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」"""

    res = punctuation.convert(
        "﹁我最贊成羅素先生的一句話：﹃須知參差多態，乃是幸福的本源。﹄大多數的參差多態都是敏於思索的人創造出來的。﹂",
        True,
        "hant",
        "hans",
    )
    res = opencc.OpenCC("t2s").convert(res)  # type: ignore
    assert res == """“我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”"""

    res = punctuation.convert(
        "“我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”",
        False,
        "hans",
        "hant",
    )
    res = opencc.OpenCC("s2t").convert(res)  # type: ignore
    assert res == """「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」"""

    res = punctuation.convert(
        "「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」",
        False,
        "hant",
        "hans",
    )
    res = opencc.OpenCC("t2s").convert(res)  # type: ignore
    assert res == """『我最赞成罗素先生的一句话：「须知参差多态，乃是幸福的本源。」大多数的参差多态都是敏于思索的人创造出来的。』"""
