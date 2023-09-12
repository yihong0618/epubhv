from epubhv import EPUBHV, list_all_epub_in_dir
from pathlib import Path

import argparse
import os


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("epub", help="file or dir that contains epub files to change")
    parser.add_argument(
        "--v",
        dest="v",
        action="store_true",
        help="change all the epub files to vertical",
    )
    parser.add_argument(
        "--h",
        dest="h",
        action="store_true",
        help="change all the epub files to hortical",
    )

    parser.add_argument(
        "--convert",
        dest="convert",
        choices=[
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
        help="""
change all the epub files to specific language


s2t: Simplified Chinese to Traditional Chinese
t2s: Traditional Chinese to Simplified Chinese
s2tw: Simplified Chinese to Traditional Chinese (Taiwan Standard)
tw2s: Traditional Chinese (Taiwan Standard) to Simplified Chinese
s2hk: Simplified Chinese to Traditional Chinese (Hong Kong variant)
hk2s: Traditional Chinese (Hong Kong variant) to Simplified Chinese
s2twp: Simplified Chinese to Traditional Chinese (Taiwan variant)
tw2sp: Traditional Chinese (Taiwan variant) to Simplified Chinese
t2tw: Traditional Chinese (OpenCC Standard) to Taiwan Standard
hk2t: Traditional Chinese (Hong Kong variant) to Traditional Chinese
t2hk: Traditional Chinese (OpenCC Standard) to Hong Kong variant
t2jp: Traditional Chinese Characters (Kyūjitai) to New Japanese Kanji
jp2t: New Japanese Kanji to Traditional Chinese Characters (Kyūjitai)
tw2t: Traditional Chinese (OpenCC Standard) to Traditional Chinese (Taiwan standard)
        """,
    )

    options = parser.parse_args()
    epub_files = Path(options.epub)
    # default is to to_vertical
    method = "to_vertical"
    if options.h:
        method = "to_horizontal"
    elif options.v:
        method = "to_vertical"
    if epub_files.exists():
        if epub_files.is_dir():
            files = list_all_epub_in_dir(epub_files)
            for f in files:
                print(f"{str(f)} is {method}")
                try:
                    e = EPUBHV(f, convert_to=options.convert)
                    e.run(method)
                except Exception as e:
                    print(f"{str(f)} {method} is failed by {str(e)}")
        else:
            print(f"{str(epub_files)} is {method}")
            e = EPUBHV(epub_files, convert_to=options.convert)
            e.run(method)
    else:
        raise Exception("Please make sure it is a dir contains epub or is a epub file.")


if __name__ == "__main__":
    main()
