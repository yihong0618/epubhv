from setuptools import setup

setup(
    name="epubhv",
    author="yihong0618",
    author_email="zouzou0208@gmail.com",
    url="https://github.com/yihong0618/epubhv",
    license="MIT",
    version="0.2.0",
    install_requires=[
        "bs4",
        "lxml",
        "cssutils",
        "opencc-python-reimplemented",
        "soupsieve",
    ],
    entry_points={
        "console_scripts": ["epubhv = epubhv.cli:main"],
    },
)
