from epubhv import EPUBHV, list_all_epub_in_dir
from pathlib import Path

import argparse
import os


def main():
    parser = argparse.ArgumentParser()
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
                    e = EPUBHV(f)
                    e.run(method)
                except Exception as e:
                    print(f"{str(f)} {method} is failed by {str(e)}")
        else:
            print(f"{str(epub_files)} is {method}")
            e = EPUBHV(epub_files)
            e.run(method)
    else:
        raise Exception("Please make sure it is a dir contains epub or is a epub file.")


if __name__ == "__main__":
    main()
