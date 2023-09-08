import os
import shutil
from pathlib import Path

from epubhv import EPUBHV, _make_epub_files_dict, list_all_epub_in_dir


def test_find_epub_books():
    assert sorted(list_all_epub_in_dir("tests/test_epub")) == sorted(
        [
            "tests/test_epub/animal_farm.epub",
            "tests/test_epub/Liber_Esther.epub",
            "tests/test_epub/books/lemo.epub",
        ]
    )


def test_extract_epub_path():
    b = EPUBHV(Path("tests/test_epub/animal_farm.epub"))
    b.extract_one_epub_to_dir()
    assert os.path.exists(".epub_temp_dir/animal_farm")
    shutil.rmtree(".epub_temp_dir")


def test_make_files_dict():
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b.extract_one_epub_to_dir()
    d = dict(_make_epub_files_dict(".epub_temp_dir/animal_farm"))
    assert sorted(
        [".html", ".css", ".xhtml", "", ".opf", ".ncx", ".jpg", ".xml"]
    ) == sorted(list(d.keys()))
    assert 19 == len(d.get(".html", 0))
    shutil.rmtree(".epub_temp_dir")


def test_change_epub_to_vertical():
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b.run()
    assert b.opf_file == Path(".epub_temp_dir/animal_farm/content.opf")
    os.remove("animal_farm-v.epub")


def test_find_epub_css_files():
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b._make_epub_values()
    b.has_css_file == True
    assert b.has_css_file == False
    f = EPUBHV("tests/test_epub/books/lemo.epub")
    f.run("to_horizontal")
    assert os.path.exists("lemo-h.epub") is True
    os.remove("lemo-h.epub")
