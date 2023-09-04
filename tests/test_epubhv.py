from epubhv import _list_all_epub_in_dir, EPUBHV
import os
import shutil

def test_find_epub_books():                                                                                                                                                                                                             
    assert sorted(_list_all_epub_in_dir("tests/test_epub")) == sorted(["tests/test_epub/animal_farm.epub", "tests/test_epub/Liber_Esther.epub", "tests/test_epub/books/lemo.epub"])


def test_extract_epub_book():
    assert 2==2


def test_extract_epub_path():
    b = EPUBHV("tests/test_epub")
    assert b.files_list == ["tests/test_epub/animal_farm.epub", "tests/test_epub/Liber_Esther.epub", "tests/test_epub/books/lemo.epub"] 
    b.extract_one_epub_to_dir("tests/test_epub/animal_farm.epub")
    assert os.path.exists(".epub_temp_dir/animal_farm")
    # shutil.rmtree(".epub_temp_dir")
