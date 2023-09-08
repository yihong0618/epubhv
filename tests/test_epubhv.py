import os
import shutil
from pathlib import Path

from epubhv import EPUBHV, list_all_epub_in_dir, _make_epub_files_dict


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
    assert {
        ".html": [
            Path(".epub_temp_dir/animal_farm/index_split_003.html"),
            Path(".epub_temp_dir/animal_farm/index_split_015.html"),
            Path(".epub_temp_dir/animal_farm/index_split_018.html"),
            Path(".epub_temp_dir/animal_farm/index_split_014.html"),
            Path(".epub_temp_dir/animal_farm/index_split_002.html"),
            Path(".epub_temp_dir/animal_farm/index_split_009.html"),
            Path(".epub_temp_dir/animal_farm/index_split_005.html"),
            Path(".epub_temp_dir/animal_farm/index_split_013.html"),
            Path(".epub_temp_dir/animal_farm/index_split_012.html"),
            Path(".epub_temp_dir/animal_farm/index_split_004.html"),
            Path(".epub_temp_dir/animal_farm/index_split_008.html"),
            Path(".epub_temp_dir/animal_farm/index_split_011.html"),
            Path(".epub_temp_dir/animal_farm/index_split_007.html"),
            Path(".epub_temp_dir/animal_farm/index_split_006.html"),
            Path(".epub_temp_dir/animal_farm/index_split_010.html"),
            Path(".epub_temp_dir/animal_farm/index_split_017.html"),
            Path(".epub_temp_dir/animal_farm/index_split_001.html"),
            Path(".epub_temp_dir/animal_farm/index_split_000.html"),
            Path(".epub_temp_dir/animal_farm/index_split_016.html"),
        ],
        ".css": [
            Path(".epub_temp_dir/animal_farm/page_styles.css"),
            Path(".epub_temp_dir/animal_farm/stylesheet.css"),
        ],
        ".xhtml": [Path(".epub_temp_dir/animal_farm/titlepage.xhtml")],
        "": [Path(".epub_temp_dir/animal_farm/mimetype")],
        ".opf": [Path(".epub_temp_dir/animal_farm/content.opf")],
        ".ncx": [Path(".epub_temp_dir/animal_farm/toc.ncx")],
        ".jpg": [
            Path(".epub_temp_dir/animal_farm/images/00005.jpg"),
            Path(".epub_temp_dir/animal_farm/images/00002.jpg"),
            Path(".epub_temp_dir/animal_farm/images/00003.jpg"),
            Path(".epub_temp_dir/animal_farm/images/cover.jpg"),
        ],
        ".xml": [Path(".epub_temp_dir/animal_farm/META-INF/container.xml")],
    } == dict(_make_epub_files_dict(".epub_temp_dir/animal_farm"))
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
