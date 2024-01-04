
from abc import abstractmethod

import os

from pathlib import Path
from typing import List, Optional
import opencc

from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, PageElement, ResultSet, Tag
from cssutils import CSSParser
from cssutils.css import CSSStyleSheet

from epubhv.punctuation import Punctuation
from epubhv.yomituki import RubySoup, string_containers  # pyright: ignore

WRITING_KEY_LIST: List[str] = [
    "writing-mode",
    "-webkit-writing-mode",
    "-epub-writing-mode",
]
V_ITEM_TO_ADD_IN_MANIFEST: str = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)
V_STYLE_LINE: str = (
    '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
)
V_STYLE_LINE_IN_OPF: str = '<meta content="vertical-rl" name="primary-writing-mode"/>'
# same as v
H_STYLE_LINE: str = (
    '<link rel="stylesheet" href="../Style/style.css" type="text/css" />'
)
H_STYLE_LINE_IN_OPF: str = '<meta content="horizontal-lr" name="primary-writing-mode"/>'
# same as v
H_ITEM_TO_ADD_IN_MANIFEST: str = (
    '<item id="stylesheet" href="Style/style.css" media-type="text/css" />'
)


STYLE = {"vertical":{
    "page-progression-direction": "ltr",
    "style_line_in_opf":V_STYLE_LINE_IN_OPF,
    "primary-writing-mode":"vertical-rl",
    "item_to_add_in_manifest":V_ITEM_TO_ADD_IN_MANIFEST
},"horizontal":{
    "page-progression-direction": "rtl",
    "style_line_in_opf":H_STYLE_LINE_IN_OPF,
    "primary-writing-mode":"horizontal-lr",
    "item_to_add_in_manifest":H_ITEM_TO_ADD_IN_MANIFEST
}}
class Converter:

    def process_css(self, css_string):
        return css_string

    def process_content(self, content):
        return content

    def process_opf(self, soup):
        return soup
    
    def no_css(self, opf_dir):
        # do nothing
        pass

    def set_data(self, data):
        # do nothing
        pass

class Direction_Converter(Converter):
    
    def process_opf(self, soup):
        spine: Optional[Tag | NavigableString] = soup.find("spine")
        direction = self.get_direction()
        progression_direction = STYLE[direction]["page-progression-direction"]
        assert spine is not None
        if spine.attrs.get("page-progression-direction", "") != progression_direction:  # type: ignore
            spine.attrs["page-progression-direction"] = progression_direction  # type: ignore
        meta_list: ResultSet[Tag] = soup.find_all("meta")
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                m.attrs["content"] = STYLE[direction]["primary-writing-mode"]
        else:
            meta_list.append(bs(STYLE[direction]["style_line_in_opf"], "xml").contents[0])  # type: ignore
        if self._need_update_manifest == True:
            # add css item to manifest items
            soup.find_all("manifest")[0].append(
                bs(STYLE[direction]["item_to_add_in_manifest"], "xml").contents[0]
            )
        return soup
    
    def add_stylesheet_to_html(self, soup: bs, style_line):
        # Find the head section or create if not present
        head: Optional[Tag | NavigableString] = soup.find("head")
        if not head or type(head) is NavigableString:
            head = soup.new_tag("head")  # type: ignore
            soup.html.insert(0, head)  # type: ignore
        # Add the stylesheet line inside the head section
        head.append(bs(style_line, "html.parser").contents[0])

    @abstractmethod
    def get_direction(self):
        pass


class To_Vertical_Converter(Direction_Converter):
    
    def __init__(self) -> None:
        super().__init__()
        self._need_update_manifest = False
  
    def process_css(self, css_string):
        parser: CSSParser = CSSParser()
        css_sheet: CSSStyleSheet = parser.parseString(css_string)
        has_html_or_body: bool = False
        for s in css_sheet.cssRules.rulesOfType(1):  # type: ignore
            if s.selectorText == "html":  # type: ignore
                has_html_or_body = True
                for w in WRITING_KEY_LIST:
                    if w not in s.style.keys():  # type: ignore
                        # set it to vertical
                        s.style[w] = "vertical-rl"  # type: ignore
        if not has_html_or_body:
            css_sheet.add(  # type: ignore
                """
                html {
                    -epub-writing-mode: vertical-rl;
                    writing-mode: vertical-rl;
                    -webkit-writing-mode: vertical-rl;
                }
                """
            )
        return css_sheet.cssText.decode('utf-8')
    
    def get_direction(self):
        return "vertical"

    def no_css(self, opf_dir):
        # if we have no css file in the epub than we create one.
        style_path: Path = Path(opf_dir) / Path("Style")
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
        self._need_update_manifest = True
    
    def process_content(self, content):
        if self._need_update_manifest == False:
            return content
        soup: bs = bs(content, "html.parser")
        super().add_stylesheet_to_html(self, soup, V_STYLE_LINE)
        return str(soup)


class To_Horizontal_Converter(Converter):
  
    def process_css(self, css_string):
        parser: CSSParser = CSSParser()
        css_sheet: CSSStyleSheet = parser.parseString(css_string)
        for s in css_sheet.cssRules.rulesOfType(1):  # type: ignore
            for k in s.style.keys():  # type: ignore
                if k in WRITING_KEY_LIST:
                    del s.style[k]  # type: ignore
        return css_sheet.cssText.decode('utf-8')

    def get_direction(self):
        return "horizontal"

    # seems don't need this? 
    # def process_content(self, content):
    #     if self._need_update_manifest == False:
    #         return content
    #     soup: bs = bs(content, "html.parser")
    #     super().add_stylesheet_to_html(self, soup, H_STYLE_LINE)
    #     return str(soup)
    

class Language_Converter(Converter):
    
    def __init__(self):
        self.convert_punctuation: str = None
        self.converter = None
        self.convert_to = None
        self.method = None
    
    def set_data(self, data):
        if "method" in data:
            self.method = data["method"]
        if "convert_punctuation" in data:
            self.convert_punctuation: str = data["convert_punctuation"]
        if "convert_to" in data:
            self.convert_to = data["convert_to"]
            self.converter = opencc.OpenCC(self.convert_to)

    def process_opf(self, soup):
        meta_list: ResultSet[Tag] = soup.find_all("meta")
        writing_mode = None
        for m in meta_list:
            if m.attrs.get("name", "") == "primary-writing-mode":
                writing_mode = m.attrs["content"]
        if writing_mode == "vertical-rl":
            self.method = "to_vertical"
        else:
            self.method = "to_horizontal"
  
    def process_content(self, content):
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
                            punc = "s2t" if self.method == "to_vertical" else "t2t"
                            # default: convert “‘’” to 「『』」 in vertical mode,
                            # but not to “‘’” in horizontal mode
                        else:
                            punc = self.convert_to
                    source, target = punc.split("2")
                    punc_converter = Punctuation()
                    new_text = punc_converter.convert(  # type: ignore
                        new_text,
                        horizontal=self.method == "to_horizontal",
                        source_locale=punc_converter.map_locale(source),  # type: ignore
                        target_locale=punc_converter.map_locale(target),  # type: ignore
                    )
            element.string.replace_with(new_text)  # type: ignore
            html_element.replace_with(html_element)
        return str(soup.prettify())


class Ruby_Converter(Converter):
    
    def __init__(self):
        self.ruby_language = None

    def process_content(self, content):
        ruby_soup = bs(
                    content, "html.parser", string_containers=string_containers
                )
        # TODO fix this maybe support unruby
        r = RubySoup(self.ruby_language, True)
        r.ruby_soup(ruby_soup.body)
        return ruby_soup.prettify()
    
    def set_data(self, data):
        print(data)
        if "ruby_language" in data:
            self.ruby_language = data["ruby_language"]
