import os
import shutil
from pathlib import Path

from epubhv import EPUBHV, _make_epub_files_dict, list_all_epub_in_dir, Punctuation


def test_find_epub_books():
    assert sorted(list_all_epub_in_dir("tests/test_epub")) == sorted(
        [
            "tests/test_epub/animal_farm.epub",
            "tests/test_epub/Liber_Esther.epub",
            "tests/test_epub/books/lemo.epub",
            "tests/test_epub/sanguo.epub",
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
    if os.path.exists("animal_farm-v-original.epub"):
        os.remove("animal_farm-v-original.epub")
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b.run()
    assert b.opf_file == Path(".epub_temp_dir/animal_farm/content.opf")
    os.remove("animal_farm-v-original.epub")


def test_find_epub_css_files():
    if os.path.exists("lemo-h-original.epub"):
        os.remove("lemo-h-original.epub")
    b = EPUBHV("tests/test_epub/animal_farm.epub")
    b._make_epub_values()
    assert b.has_css_file is False
    b.run()
    os.remove("animal_farm-v-original.epub")
    f = EPUBHV("tests/test_epub/books/lemo.epub")
    f.run("to_horizontal")
    assert os.path.exists("lemo-h-original.epub") is True
    os.remove("lemo-h-original.epub")


def test_change_epub_covert():
    if os.path.exists("sanguo-v-s2t-v-original.epub"):
        os.remove("sanguo-v-s2t-v-original.epub")
    if os.path.exists("sanguo-v-s2t.epub"):
        os.remove("sanguo-v-s2t.epub")
    f = EPUBHV("tests/test_epub/sanguo.epub", "s2t")
    f.run("to_vertical")
    assert os.path.exists("sanguo-v-s2t.epub") is True
    q = EPUBHV("sanguo-v-s2t.epub")
    q.extract_one_epub_to_dir()
    q._make_epub_values()
    has_t_count = 0
    for html_file in (
        q.files_dict.get(".html", [])
        + q.files_dict.get(".xhtml", [])
        + q.files_dict.get(".htm", [])
    ):
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            r = f.read()
            if r.find("滾滾長江東逝水") > 0:
                has_t_count += 1
    assert has_t_count > 0
    q.run("to_vertical")
    os.remove("sanguo-v-s2t.epub")


def test_punctuation():
    import opencc

    s = """
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    ﹃我最赞成罗素先生的一句话：﹁须知参差多态，乃是幸福的本源。﹂大多数的参差多态都是敏于思索的人创造出来的。﹄
    """
    t = """
    「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」
    ﹁我最贊成羅素先生的一句話：﹃須知參差多態，乃是幸福的本源。﹄大多數的參差多態都是敏於思索的人創造出來的。﹂
    """

    punctuation = Punctuation()

    res = punctuation.convert(s, 'HORIZONTAL', 'hans', 'hant')
    res = opencc.OpenCC('s2t').convert(res)
    assert res == """
    「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」
    「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」
    """

    res = punctuation.convert(t, 'HORIZONTAL', 'hant', 'hans')
    res = opencc.OpenCC('t2s').convert(res)
    assert res == """
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    """

    res = punctuation.convert(s, 'VERTICAL', 'hans', 'hant')
    res = opencc.OpenCC('s2t').convert(res)
    assert res == """
    「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」
    「我最贊成羅素先生的一句話：『須知參差多態，乃是幸福的本源。』大多數的參差多態都是敏於思索的人創造出來的。」
    """

    res = punctuation.convert(t, 'VERTICAL', 'hant', 'hans')
    res = opencc.OpenCC('t2s').convert(res)
    assert res == """
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    """

    res = punctuation.convert(s, 'VERTICAL', 'hans', 'hans')
    assert res == """
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    “我最赞成罗素先生的一句话：‘须知参差多态，乃是幸福的本源。’大多数的参差多态都是敏于思索的人创造出来的。”
    """
    os.remove("sanguo-v-s2t-v-original.epub")
