import base64
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from epubhv import EPUBHV

LABELS = {
    "none": "None",
    "auto": "Auto",
    "s2t": "Simplified Chinese to Traditional Chinese",
    "t2s": "Traditional Chinese to Simplified Chinese",
    "s2tw": "Simplified Chinese to Traditional Chinese (Taiwan Standard)",
    "tw2s": "Traditional Chinese (Taiwan Standard) to Simplified Chinese",
    "s2hk": "Simplified Chinese to Traditional Chinese (Hong Kong variant)",
    "hk2s": "Traditional Chinese (Hong Kong variant) to Simplified Chinese",
    "s2twp": "Simplified Chinese to Traditional Chinese (Taiwan variant)",
    "tw2sp": "Traditional Chinese (Taiwan variant) to Simplified Chinese",
    "t2tw": "Traditional Chinese (OpenCC Standard) to Taiwan Standard",
    "hk2t": "Traditional Chinese (Hong Kong variant) to Traditional Chinese",
    "t2hk": "Traditional Chinese (OpenCC Standard) to Hong Kong variant",
    "t2jp": "Traditional Chinese Characters (Kyūjitai) to New Japanese Kanji",
    "jp2t": "New Japanese Kanji to Traditional Chinese Characters (Kyūjitai)",
    "tw2t": "Traditional Chinese (OpenCC Standard) to Traditional Chinese (Taiwan standard)",
}


def download_button(data: bytes, download_filename: str) -> None:
    b64 = base64.b64encode(data).decode()

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script>
        const a = document.createElement('a')
        a.setAttribute('href', "data:text/csv;base64,{b64}")
        a.setAttribute('download', "{download_filename}")
        a.click()
    </script>
    </head>
    </html>
    """
    components.html(dl_link, height=0)


st.set_page_config(
    page_title="EPUBHV, a toolset to convert your EPUB",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.header("📖 EPUBHV, a toolset to convert your EPUB", divider="rainbow")
st.caption(
    "Author: [@yihong0618](https://github.com/yihong0618) | [GitHub](https://github.com/yihong0618/epubhv) | [PyPI](https://pypi.org/project/epubhv/)",
)


def run():
    if st.session_state["epubfile"] is None:
        st.error("Please upload an epub file")
        return
    epubfile = st.session_state["epubfile"]
    with tempfile.TemporaryDirectory() as tmpdir, st.spinner("Processing..."):
        with open(Path(tmpdir) / epubfile.name, "wb") as f:
            f.write(epubfile.read())
        convert = st.session_state["convert"]
        epubhv = EPUBHV(
            file_path=Path(tmpdir) / epubfile.name,
            need_ruby=st.session_state["need_ruby"],
            need_cantonese=st.session_state["need_cantonese"],
            convert_to=None if convert == "none" else convert,
            convert_punctuation=st.session_state["punctuation"],
        )
        result = epubhv.run(method=st.session_state["method"], dest=Path(tmpdir))
        download_button(result.read_bytes(), result.name)


with st.form(key="my_form"):
    epubfile = st.file_uploader("Upload an epub file", type="epub", key="epubfile")
    method = st.radio(
        "Choose a method",
        ("to_vertical", "to_horizontal"),
        format_func=lambda x: x.replace("_", " ").title(),
        horizontal=True,
        key="method",
    )
    need_ruby = st.checkbox("Need ruby", key="need_ruby")
    need_cantonese = st.checkbox("Need cantonese", key="need_cantonese")

    convert = st.selectbox(
        "Transform text",
        options=[
            "none",
            "s2t",
            "t2s",
            "s2tw",
            "tw2s",
            "s2hk",
            "hk2s",
            "s2twp",
            "tw2sp",
            "t2tw",
            "hk2t",
            "t2hk",
            "t2jp",
            "jp2t",
            "tw2t",
        ],
        format_func=LABELS.__getitem__,
        key="convert",
    )
    punctuation = st.selectbox(
        "Transform punctuation",
        options=["auto", "t2s", "s2t", "none"],
        format_func=LABELS.__getitem__,
        key="punctuation",
    )
    st.form_submit_button(label="Transform", on_click=run)
