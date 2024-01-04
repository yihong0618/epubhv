from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import cast

from epubhv.epubhv import EPUBHV, list_all_epub_in_dir


class Options:
    epub: str
    method: str
    convert: str
    punctuation: str
    ruby: bool
    cantonese: bool
    dest: Path


def main() -> None:
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("epub", help="file or dir that contains epub files to change")
    parser.add_argument(
        "--v",
        dest="method",
        action="store_const",
        const="to_vertical",
        default="to_vertical",
        help="change all the epub files to vertical.",
    )
    parser.add_argument(
        "--h",
        dest="method",
        action="store_const",
        const="to_horizontal",
        help="change all the epub files to hortical.",
    )
    parser.add_argument(
        "--ruby",
        dest="ruby",
        action="store_true",
        help="Ruby it for Chinese and Japanese.",
    )
    parser.add_argument(
        "--cantonese",
        dest="cantonese",
        action="store_true",
        help="Ruby it for cantonese.",
    )
    parser.add_argument(
        "-d",
        "--dest",
        help="destination dir to save the epub files, default to current directory",
        default=".",
        type=Path,
    )

    parser.add_argument(
        "--punctuation",
        dest="punctuation",
        choices=["auto", "t2s", "s2t", "none"],
        default="auto",
        help="""convert punctuation to specific locale and direction (default: auto)

        none: do not convert based on the direction
        other options convert between vertical and horizontal punctuation
        """,
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

    options = cast(Options, parser.parse_args())
    epub_files = Path(options.epub)
    if epub_files.exists():
        if epub_files.is_dir():
            files: set[Path] = list_all_epub_in_dir(path=epub_files)
            f: Path
            for f in files:
                print(f"{str(f)} is {options.method}")
                try:
                    epubhv: EPUBHV = EPUBHV(
                        file_path=f,
                        convert_to=options.convert,
                        convert_punctuation=options.punctuation,
                        need_ruby=options.ruby,
                        need_cantonese=options.cantonese,
                    )
                    epubhv.run(method=options.method, dest=options.dest)
                except Exception as e:
                    print(f"{str(f)} {options.method} is failed by {str(e)}")
        else:
            print(f"{str(epub_files)} is {options.method}")
            epubhv: EPUBHV = EPUBHV(
                file_path=epub_files,
                convert_to=options.convert,
                need_ruby=options.ruby,
                need_cantonese=options.cantonese,
            )
            epubhv.run(method=options.method, dest=options.dest)
    else:
        raise Exception("Please make sure it is a dir contains epub or is a epub file.")


if __name__ == "__main__":
    main()
