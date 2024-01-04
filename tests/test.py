
from pathlib import Path
from epubhv.epub_processer import Epub_Processer
from epubhv.converter import Language_Converter, Ruby_Converter, To_Horizontal_Converter, To_Vertical_Converter

def test_to_vertical() -> None:
    lemo_output = Path("tmp/animal_farm_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/animal_farm.epub"))
    processer.process([To_Vertical_Converter()])
    processer.pack()
    assert lemo_output.exists()
    lemo_output.unlink(True)

# test_to_vertical()
    
def test_to_horizontal() -> None:
    lemo_output = Path("tmp/lemo_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/books/lemo.epub"))
    processer.process([To_Horizontal_Converter()])
    processer.pack()
    assert lemo_output.exists()
    lemo_output.unlink(True)

# test_to_horizontal()


def test_ruby() -> None:
    lemo_output = Path("tmp/lemo_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/books/lemo.epub"), need_ruby=True)
    processer.process([Ruby_Converter()])
    processer.pack()
    assert lemo_output.exists()
    # lemo_output.unlink(True)

# test_ruby()
    

def test_ruby_to_horizontal() -> None:
    lemo_output = Path("tmp/lemo_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/books/lemo.epub"), need_ruby=True)
    processer.process([Ruby_Converter(), To_Horizontal_Converter()])
    processer.pack()
    assert lemo_output.exists()
    lemo_output.unlink(True)

# test_ruby_to_horizontal()


def test_language_converter() -> None:
    lemo_output = Path("tmp/sanguo_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/sanguo.epub"), "s2t")
    processer.process([Language_Converter()])
    processer.pack()
    assert lemo_output.exists()
    lemo_output.unlink(True)

# test_ruby_convert_to()


def test_language_ruby_vertical_converter() -> None:
    lemo_output = Path("tmp/sanguo_output.epub")
    lemo_output.unlink(True)
    processer : Epub_Processer = Epub_Processer(Path("tests/test_epub/sanguo.epub"), "s2t", need_ruby=True)
    # TODO Actually there's problem here, if Direction_Converter comes after Language_Converter, punctuations will be wrong.
    processer.process([To_Vertical_Converter(), Language_Converter(), Ruby_Converter()])
    processer.pack()
    assert lemo_output.exists()
    lemo_output.unlink(True)

# test_language_ruby_vertical_converter()
