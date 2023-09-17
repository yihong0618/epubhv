"""
Follow these steps to change epub books to vertical or horizontal.

"""
import logging
import os
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional

import cssutils
from cssutils import CSSParser
from cssutils.css import CSSStyleSheet
import opencc
from bs4 import BeautifulSoup as bs, NavigableString, PageElement, ResultSet, Tag

from epubhv.punctuation import Punctuation

cssutils.log.setLevel(logging.CRITICAL)  # type: ignore

WRITING_KEY_LIST: List[str] = [
    "writing-mode",
    "-webkit-writing-mode",
    "-epub-writing-mode",
]
V_STYLE_LINE: str = (
    '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
)
# same as v
H_STYLE_LINE: str = (
    '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
)
V_STYLE_LINE_IN_OPF: str = '<meta content="vertical-rl" name="primary-writing-mode"/>'
H_STYLE_LINE_IN_OPF: str = '<meta content="horizontal-lr" name="primary-writing-mode"/>'
V_ITEM_TO_ADD_IN_MANIFEST: str = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)
# same as v
H_ITEM_TO_ADD_IN_MANIFEST: str = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)


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


class EPUBHV:
    def __init__(
        self,
        file_path: Path,
        convert_to: Optional[str] = None,
        convert_punctuation: Optional[str] = "auto",
    ) -> None:
        # declare instance fields
        self.epub_file: Path
        self.has_css_file: bool = False
        self.files_dict: Dict[str, List[Path]] = {}
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

    @staticmethod
    def _add_stylesheet_to_html(html_file_path: Path, stylesheet_line: str):
        with open(html_file_path, "r", encoding="utf-8", errors="ignore") as file:
            content: str = file.read()

        soup: bs = bs(content, "html.parser")

        # Find the head section or create if not present
        head: Optional[Tag | NavigableString] = soup.find("head")
        if not head or type(head) is NavigableString:
            head = soup.new_tag("head")  # type: ignore
            soup.html.insert(0, head)  # type: ignore

        # Add the stylesheet line inside the head section
        head.append(bs(stylesheet_line, "html.parser").contents[0])

        with open(html_file_path, "w", encoding="utf-8", errors="ignore") as file:
            file.write(str(soup))

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
        opf_files = self.files_dict.get(".opf", [])
        assert len(opf_files) == 1, "Epub must have only one opf file"
        self.opf_file = opf_files[0]
        self.opf_dir = self.opf_file.parent.absolute()

    def change_epub_to_vertical(self) -> None:
        """
        steps:
          1. check if have CSS files
          2. check the epub spine `page-progression-direction` add to it
          3. check `primary-writing-mode` in opf file's meta, if have change it to vertical-rl, if not add it.
          4. if we have add CSS files we need to check if have `html` attribute
          5. if have `html` attribute add vertical-rl to it
          6. if have not `html` we add it
          7. if we do not have css file, we add one with html `vertical-rl` and change all the html to add the css files
        """
        soup: bs = load_opf_meta_data(self.opf_file)
        # change it to rtl -> right to left
        spine: Optional[Tag | NavigableString] = soup.find("spine")
        assert spine is not None
        if spine.attrs.get("page-progression-direction", "") != "rtl":  # type: ignore
            spine.attrs["page-progression-direction"] = "rtl"  # type: ignore
        meta_list: ResultSet[Tag] = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = "vertical-rl"
        else:
            meta_list.append(bs(V_STYLE_LINE_IN_OPF, "xml").contents[0])  # type: ignore

        manifest: Tag = soup.find_all("manifest")[0]
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
                c: CSSParser = CSSParser()
                p: CSSStyleSheet = c.parseFile(css)  # type: ignore
                has_html_or_body: bool = False
                for s in p.cssRules.rulesOfType(1):  # type: ignore
                    if s.selectorText == "html":  # type: ignore
                        has_html_or_body = True
                        for w in WRITING_KEY_LIST:
                            if w not in s.style.keys():  # type: ignore
                                # set it to vertical
                                s.style[w] = "vertical-rl"  # type: ignore
                if not has_html_or_body:
                    p.add(  # type: ignore
                        """
                        html {
                            -epub-writing-mode: vertical-rl;
                            writing-mode: vertical-rl;
                            -webkit-writing-mode: vertical-rl;
                        }
                        """
                    )
                css_style = p.cssText  # type: ignore
                with open(css, "wb") as file:
                    file.write(css_style)  # type: ignore
        else:
            # if we have no css file in the epub than we create one.
            style_path: Path = Path(self.opf_dir) / Path("Style")
            if not style_path.exists():
                os.mkdir(style_path)
            new_css_file: Path = style_path / Path("style.css")
            with open(new_css_file, "w", encoding="utf-8", errors="ignore") as file:
                file.write(
                    """
@charset "utf-8";
html {
  -epub-writing-mode: vertical-rl;
  writing-mode: vertical-rl;
  -webkit-writing-mode: vertical-rl;
}
                        """
                )
            # add css item to manifest items
            soup.find_all("manifest")[0].append(
                bs(V_ITEM_TO_ADD_IN_MANIFEST, "xml").contents[0]
            )
            # then we need to change all html files
            f: Path
            for f in (
                self.files_dict.get(".html", [])
                + self.files_dict.get(".xhtml", [])
                + self.files_dict.get(".htm", [])
            ):
                self._add_stylesheet_to_html(
                    html_file_path=f, stylesheet_line=V_STYLE_LINE
                )
        with open(self.opf_file, "w", encoding="utf-8", errors="ignore") as file:
            file.write(str(soup))

    def change_epub_to_horizontal(self) -> None:
        """
        steps:
          1. check if have CSS files
          2. check the epub spine `page-progression-direction` add to it
          3. check `primary-writing-mode` in opf file's meta, if have change it to horizontal-rl, if not add it.
          4. check all css files and remove all "writing-mode", "-webkit-writing-mode", "-epub-writing-mode" to make it default that is horizontal
        """
        soup: bs = load_opf_meta_data(self.opf_file)
        # change it to ltr -> left to right
        spine: Optional[Tag | NavigableString] = soup.find("spine")
        assert spine is not None
        if spine.attrs.get("page-progression-direction", "") != "ltr":  # type: ignore
            spine.attrs["page-progression-direction"] = "ltr"  # type: ignore
        meta_list: ResultSet[Tag] = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = "horizontal-lr"
        else:
            meta_list.append(bs(H_STYLE_LINE_IN_OPF, "xml").contents[0])  # type: ignore
        with open(self.opf_file, "w", encoding="utf-8", errors="ignore") as file:
            file.write(str(soup))

        manifest: Tag = soup.find_all("manifest")[0]
        items = [i for i in manifest.find_all("item")]
        self.css_files = [
            self.opf_dir / Path(i.attrs.get("href", ""))
            for i in items
            if i.attrs.get("media-type", "") == "text/css"
        ]
        self.has_css_file = len(self.css_files) > 0
        if self.has_css_file:
            for css in self.css_files:
                c: CSSParser = CSSParser()
                p: CSSStyleSheet = c.parseFile(css)  # type: ignore
                for s in p.cssRules.rulesOfType(1):  # type: ignore
                    for k in s.style.keys():  # type: ignore
                        if k in WRITING_KEY_LIST:
                            del s.style[k]  # type: ignore
                css_style = p.cssText  # type: ignore
                with open(css, "wb") as file:
                    file.write(css_style)  # type: ignore

    def convert(self, method: str = "to_vertical") -> None:
        if self.converter is None:
            return

        html_file: Path
        for html_file in (
            self.files_dict.get(".html", [])
            + self.files_dict.get(".xhtml", [])
            + self.files_dict.get(".htm", [])
        ):
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                content: str = f.read()
            soup: bs = bs(content, "html.parser")

            html_element: Optional[Tag | NavigableString] = soup.find("html")
            assert html_element is not None
            text_elements: ResultSet[PageElement] = html_element.find_all(string=True)  # type: ignore

            element: Tag
            for element in text_elements:  # type: ignore
                old_text = element.string
                if old_text is not None:
                    new_text = self.converter.convert(old_text)  # type: ignore
                    punc = self.convert_punctuation
                    if punc != "none":
                        if punc == "auto":
                            if self.convert_to is None:
                                punc = "s2t" if method == "to_vertical" else "t2t"
                                # default: convert “‘’” to 「『』」 in vertical mode,
                                # but not to “‘’” in horizontal mode
                            else:
                                punc = self.convert_to
                        source, target = punc.split("2")
                        punc_converter = Punctuation()
                        new_text = punc_converter.convert(  # type: ignore
                            new_text,
                            horizontal=method == "to_horizontal",
                            source_locale=punc_converter.map_locale(source),  # type: ignore
                            target_locale=punc_converter.map_locale(target),  # type: ignore
                        )
                element.string.replace_with(new_text)  # type: ignore
                html_element.replace_with(html_element)

            with open(html_file, "w", encoding="utf-8") as file:
                html_element.replace_with(html_element)

            with open(html_file, "w", encoding="utf-8", errors="ignore") as file:
                file.write(soup.prettify())

    def pack(self, method: str = "to_vertical") -> None:
        lang: str = "original"
        if self.convert_to is not None:
            lang = self.convert_to
        if method == "to_vertical":
            book_name_v: str = f"{self.book_name}-v-{lang}.epub"
        else:
            book_name_v: str = f"{self.book_name}-h-{lang}.epub"

        shutil.make_archive(
            base_name=book_name_v, format="zip", root_dir=self.book_path
        )
        os.rename(src=book_name_v + ".zip", dst=book_name_v)
        shutil.rmtree(self.book_path)

    def run(self, method: str = "to_vertical") -> None:
        assert method in [
            "to_horizontal",
            "to_vertical",
        ], "must be to_horizontal or to_vertical."
        ### make the basic epub value we need ###
        self.make_epub_values()
        if method == "to_vertical":
            self.change_epub_to_vertical()
        elif method == "to_horizontal":
            self.change_epub_to_horizontal()
        else:
            raise Exception("Only support epub to vertical or horizontal for now")

        self.convert(method=method)
        self.pack(method=method)
