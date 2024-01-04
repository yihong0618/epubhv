"""
Follow these steps to change epub books to vertical or horizontal.
"""
import logging
import os
import shutil
import zipfile
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional

import cssutils
import opencc
from bs4 import BeautifulSoup as bs, Tag

from langdetect import detect, LangDetectException

cssutils.log.setLevel(logging.CRITICAL)  # type: ignore

def list_all_epub_in_dir(path: Path) -> set[Path]:
    return set(path.rglob("*.epub"))


def make_epub_files_dict(dir_path: Path) -> Dict[str, List[Path]]:
    files_dict: Dict[str, List[Path]] = defaultdict(list)
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            files_dict[Path(filename).suffix].append(Path(root) / Path(filename))
    return files_dict


def load_opf_meta_data(opf_file: Path) -> bs:
    with open(opf_file, encoding="utf-8", errors="ignore") as f:
        content: str = f.read()
        soup: bs = bs(content, "xml")
    return soup


class Epub_Processer:
    def __init__(
        self,
        file_path: Path,
        convert_to: Optional[str] = None,
        convert_punctuation: Optional[str] = "auto",
        need_ruby: bool = False,
        need_cantonese: bool = False,
    ) -> None:
        # declare instance fields
        self.epub_file: Path
        self.has_css_file: bool = False
        # for language ruby
        self.need_ruby: bool = need_ruby
        self.ruby_language = None
        self.cantonese = need_cantonese
        self.files_dict: Dict[str, List[Path]] = {}
        self.content_files_list: List[Path] = []
        self.book_path: Path
        self.book_name: str
        self.opf_file: Path
        self.converter: Optional[opencc.OpenCC]
        self.convert_to: Optional[str]
        self.convert_punctuation: str = "auto"

        # initialize instance fields
        self.epub_file = file_path
        if convert_to is not None:
            self.converter = opencc.OpenCC(convert_to)
            self.convert_to = convert_to
        else:
            self.converter = None
            self.convert_to = None
        if convert_punctuation:
            self.convert_punctuation = convert_punctuation

    def extract_one_epub_to_dir(self) -> None:
        assert self.epub_file.suffix == ".epub", f"{self.epub_file} Must be epub file"
        book_name: str = self.epub_file.name.split(".")[0]
        self.book_name = book_name
        book_path = Path(".epub_temp_dir") / Path(book_name)
        Path(".epub_temp_dir").mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.epub_file) as f:
            f.extractall(book_path)
        self.book_path = book_path

    def make_epub_values(self) -> None:
        """
        setups:
          1. extract the epub files
          2. make the file dict
          3. find the key file -> opf file
          4. find if has css file and make all css files to list
        """
        self.extract_one_epub_to_dir()
        self.files_dict = make_epub_files_dict(self.book_path)
        self.content_files_list = (
            self.files_dict.get(".html", [])
            + self.files_dict.get(".xhtml", [])
            + self.files_dict.get(".htm", [])
        )
        opf_files = self.files_dict.get(".opf", [])
        assert len(opf_files) == 1, "Epub must have only one opf file"
        self.opf_file = opf_files[0]
        self.opf_dir = self.opf_file.parent.absolute()

    def __detect_language(self):
        c = Counter()
        for f in self.content_files_list:
            with open(f, "r", encoding="utf-8", errors="ignore") as f:
                content: str = f.read()
            sp: bs = bs(content, "html.parser")
            if sp.body:
                body_text: str = sp.body.get_text()
                try:
                    language = detect(body_text)
                    c[language] += 1
                except LangDetectException:
                    pass
        if c:
            language = c.most_common()[0][0]
            # WTF sometimes Chinese will detect as ko?
            # TODO change to a better detect
            if language in ["ko", "zh-tw"]:
                self.ruby_language = "cantonese" if self.cantonese else language
                self.need_ruby = True
            elif language in ["ja"]:
                self.ruby_language = "ja"
                self.need_ruby = True
            elif language in ["zh", "zh-cn"]:
                self.ruby_language = "zh"
                self.need_ruby = True

    def _make_ruby_language(self, soup):
        if self.need_ruby:
            # if we need ruby we need to find the ruby language
            languages = soup.find("dc:language")
            if languages and 0:
                language = languages.contents[0]
                if language in ["ja", "zh", "zh-cn"]:
                    self.ruby_language = language
                    self.need_ruby = True
                else:
                    print(
                        f"Ruby feature do not support this language -> {language}, \n for book: {self.book_name} we will ignore it."
                    )
                    self.need_ruby = False
            else:
                self.__detect_language()
                if not self.ruby_language:
                    print(
                        "There's no language meta data in meta file and can not detect the language, we use Japanese as default. we can not ruby it"
                    )
                    self.need_ruby = False

    def process(self, converters:[]):
        self.make_epub_values()
        for converter in converters:
            converter.set_data({
                "convert_to" : self.convert_to,
                "convert_punctuation": self.convert_punctuation
            })
        with open(self.opf_file, "r", encoding="utf-8", errors="ignore") as opf_file:
            opf_content: str = opf_file.read()
            opfSoup: bs = bs(opf_content, "xml")
            self._make_ruby_language(opfSoup)
            for converter in converters:
                converter.set_data({
                    "ruby_language" : self.ruby_language,
                })
            manifest: Tag = opfSoup.find_all("manifest")[0]
            items = [i for i in manifest.find_all("item")]
            self.css_files = [
                self.opf_dir / Path(i.attrs.get("href", ""))
                for i in items
                if i.attrs.get("media-type", "") == "text/css"
            ]
            
            self.has_css_file = len(self.css_files) > 0
            if self.has_css_file:
                css: Path
                for css in self.css_files:
                    with open(css, "r", encoding="utf-8", errors="ignore") as css_file:
                        css_content: str = css_file.read()
                        for converter in converters:
                            css_content = converter.process_css(css_content)
                    with open(css, "w", encoding="utf-8", errors="ignore") as css_file:
                        css_file.write(css_content)
            else:
                for converter in converters:
                    converter.no_css(self.opf_dir)

            # css process should before opf process，because update manifest in opf process depends on converter.no_css()
            for converter in converters:
                converter.process_opf(opfSoup)
            
        with open(self.opf_file, 'w') as opf_file:
            opf_file.write(str(opfSoup))

        for html_file_path in self.content_files_list:
            with open(html_file_path, "r", encoding="utf-8", errors="ignore") as content_file:
                content: str = content_file.read()
                for converter in converters:
                    content = converter.process_content(content)
            with open(html_file_path, "w", encoding="utf-8", errors="ignore") as content_file:
                content_file.write(content)
                
    def pack(self) -> None:
        dest = "tmp"
        # lang: str = "original"
        # if self.convert_to is not None:
        #     lang = self.convert_to
        # if self.need_ruby:
        #     lang = f"{lang}-ruby"
        # if method == "to_vertical":
        #     book_name: str = f"{self.book_name}-v-{lang}.epub"
        # elif method == "to_horizontal":
        #     book_name: str = f"{self.book_name}-h-{lang}.epub"
        # else:
        #     book_name: str = f"{self.book_name}-{lang}.epub"
        book_name: str = f"{dest}/{self.book_name}_output.epub"
        shutil.make_archive(base_name=book_name, format="zip", root_dir=self.book_path)
        os.rename(src=book_name + ".zip", dst=book_name)
        shutil.rmtree(self.book_path)
        return book_name
