"""
Follow these steps to change epub books to vertical or horizontal.

"""
import logging
import os
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path

import cssutils
import opencc
from bs4 import BeautifulSoup as bs

cssutils.log.setLevel(logging.CRITICAL)

WRITING_KEY_LIST = ["writing-mode", "-webkit-writing-mode", "-epub-writing-mode"]
V_STYLE_LINE = '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
# same as v
H_STYLE_LINE = '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
V_STYLE_LINE_IN_OPF = '<meta content="vertical-rl" name="primary-writing-mode"/>'
H_STYLE_LINE_IN_OPF = '<meta content="horizontal-lr" name="primary-writing-mode"/>'
V_ITEM_TO_ADD_IN_MANIFEST = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)
# same as v
H_ITEM_TO_ADD_IN_MANIFEST = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)


def list_all_epub_in_dir(path):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def _make_epub_files_dict(dir_path):
    files_dict = defaultdict(list)
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            files_dict[Path(filename).suffix].append(Path(root) / Path(filename))
    return files_dict


def load_opf_meta_data(opf_file):
    with open(opf_file, encoding="utf-8") as f:
        content = f.read()
        soup = bs(content, "xml")
    return soup


class EPUBHV:
    def __init__(self, file_name, convert_to=None):
        self.epub_file = Path(file_name)
        self.has_css_file = False
        self.files_dict = {}
        self.book_path = None
        self.book_name = None
        self.opf_file = None
        if convert_to is not None:
            self.converter = opencc.OpenCC(convert_to)
            self.convert_to = convert_to
        else:
            self.converter = None
            self.convert_to = None

    def extract_one_epub_to_dir(self):
        assert self.epub_file.suffix == ".epub", f"{self.epub_file} Must be epub file"
        book_name = self.epub_file.name.split(".")[0]
        self.book_name = book_name
        book_path = Path(".epub_temp_dir") / Path(book_name)
        if not Path(".epub_temp_dir").exists():
            os.mkdir(".epub_temp_dir")
        with zipfile.ZipFile(self.epub_file) as f:
            f.extractall(book_path)
        self.book_path = book_path

    @staticmethod
    def _add_stylesheet_to_html(html_file_path, stylesheet_line):
        with open(html_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        soup = bs(content, "html.parser")

        # Find the head section or create if not present
        head = soup.find("head")
        if not head:
            head = soup.new_tag("head")
            soup.html.insert(0, head)

        # Add the stylesheet line inside the head section
        head.append(bs(stylesheet_line, "html.parser").contents[0])

        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

    def _make_epub_values(self):
        """
        setups:
          1. extract the epub files
          2. make the file dict
          3. find the key file -> opf file
          4. find if has css file and make all css files to list
        """
        self.extract_one_epub_to_dir()
        self.files_dict = _make_epub_files_dict(self.book_path)
        opf_files = self.files_dict.get(".opf", [])
        assert len(opf_files) == 1, "Epub must have only one opf file"
        self.opf_file = opf_files[0]
        self.opf_dir = self.opf_file.parent.absolute()

    def change_epub_to_vertical(self):
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
        soup = load_opf_meta_data(self.opf_file)
        # change it to rtl -> right to left
        spine = soup.find("spine")
        if spine.attrs.get("page-progression-direction", "") != "rtl":
            spine.attrs["page-progression-direction"] = "rtl"
        meta_list = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = "vertical-rl"
        else:
            meta_list.append(bs(V_STYLE_LINE_IN_OPF, "xml").contents[0])
        with open(self.opf_file, "w", encoding="utf-8") as file:
            file.write(str(soup))

        manifest = soup.find_all("manifest")[0]
        items = [i for i in manifest.find_all("item")]
        self.css_files = [
            self.opf_dir / Path(i.attrs.get("href", ""))
            for i in items
            if i.attrs.get("media-type", "") == "text/css"
        ]
        self.has_css_file = len(self.css_files) > 0
        if self.has_css_file:
            for css in self.css_files:
                c = cssutils.CSSParser()
                p = c.parseFile(css)
                has_html_or_body = False
                for s in p.cssRules.rulesOfType(1):
                    if s.selectorText == "html":
                        has_html_or_body = True
                        for w in WRITING_KEY_LIST:
                            if w not in s.style.keys():
                                # set it to vertical
                                s.style[w] = "vertical-rl"
                if not has_html_or_body:
                    p.add(
                        "html {-epub-writing-mode: vertical-rl; writing-mode: vertical-rl; -webkit-writing-mode: vertical-rl}"
                    )
                css_style = p.cssText
                with open(css, "wb") as f:
                    f.write(css_style)
        else:
            # if we have no css file in the epub than we create one.
            style_path = Path(self.opf_dir) / Path("Style")
            if not style_path.exists():
                os.mkdir(style_path)
            new_css_file = style_path / Path("style.css")
            with open(new_css_file, "w", encoding="utf-8") as f:
                f.write(
                    """
@charset "utf-8";
html {
  -epub-writing-mode: vertical-rl;
  writing-mode: vertical-rl;
  -webkit-writing-mode: vertical-rl
}
                        """
                )
            # add css item to manifest items
            soup.find_all("manifest")[0].append(
                bs(V_ITEM_TO_ADD_IN_MANIFEST, "xml").contents[0]
            )
            # then we need to change all html files
            for f in (
                self.files_dict.get(".html", [])
                + self.files_dict.get(".xhtml", [])
                + self.files_dict.get(".htm", [])
            ):
                self._add_stylesheet_to_html(f, V_STYLE_LINE)

    def change_epub_to_horizontal(self):
        """
        steps:
          1. check if have CSS files
          2. check the epub spine `page-progression-direction` add to it
          3. check `primary-writing-mode` in opf file's meta, if have change it to horizontal-rl, if not add it.
          4. check all css files and remove all "writing-mode", "-webkit-writing-mode", "-epub-writing-mode" to make it default that is horizontal
        """
        soup = load_opf_meta_data(self.opf_file)
        # change it to ltr -> left to right
        spine = soup.find("spine")
        if spine.attrs.get("page-progression-direction", "") != "ltr":
            spine.attrs["page-progression-direction"] = "ltr"
        meta_list = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = "horizontal-lr"
        else:
            meta_list.append(bs(H_STYLE_LINE_IN_OPF, "xml").contents[0])
        with open(self.opf_file, "w", encoding="utf-8") as file:
            file.write(str(soup))

        manifest = soup.find_all("manifest")[0]
        items = [i for i in manifest.find_all("item")]
        self.css_files = [
            self.opf_dir / Path(i.attrs.get("href", ""))
            for i in items
            if i.attrs.get("media-type", "") == "text/css"
        ]
        self.has_css_file = len(self.css_files) > 0
        if self.has_css_file:
            for css in self.css_files:
                c = cssutils.CSSParser()
                p = c.parseFile(css)
                for s in p.cssRules.rulesOfType(1):
                    for k in s.style.keys():
                        if k in WRITING_KEY_LIST:
                            del s.style[k]
                css_style = p.cssText
                with open(css, "wb") as f:
                    f.write(css_style)

    def convert(self):
        if self.converter is None:
            return

        for html_file in (
            self.files_dict.get(".html", [])
            + self.files_dict.get(".xhtml", [])
            + self.files_dict.get(".htm", [])
        ):
            with open(html_file, "r") as f:
                content = f.read()
            soup = bs(content, "html.parser")

            html_element = soup.find("html")
            text_elements = html_element.find_all(string=True)

            for element in text_elements:
                old_text = element.string
                if old_text is not None:
                    new_text = self.converter.convert(old_text)
                    element.string.replace_with(new_text)
            html_element.replace_with(html_element)

            with open(html_file, "w") as file:
                file.write(soup.prettify())

    def pack(self, method="to_vertical"):
        lang = "original"
        if self.convert_to is not None:
            lang = self.convert_to
        if method == "to_vertical":
            book_name_v = f"{self.book_name}-v-{lang}.epub"
        else:
            book_name_v = f"{self.book_name}-h-{lang}.epub"

        shutil.make_archive(book_name_v, "zip", self.book_path)
        os.rename(book_name_v + ".zip", book_name_v)
        shutil.rmtree(self.book_path)

    def run(self, method="to_vertical"):
        assert method in [
            "to_horizontal",
            "to_vertical",
        ], "must be to_horizontal or to_vertical."
        ### make the basic epub value we need ###
        self._make_epub_values()
        if method == "to_vertical":
            self.change_epub_to_vertical()
        elif method == "to_horizontal":
            self.change_epub_to_horizontal()
        else:
            raise Exception("Only support epub to vertical or horizontal for now")

        self.convert()
        self.pack(method=method)
