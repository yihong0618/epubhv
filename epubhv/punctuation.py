import re
from typing import Dict, Literal


class Punctuation:
    def convert(
        self, text: str, horizontal: bool, source_locale: str, target_locale: str
    ) -> str:
        if horizontal:
            # Horizontal punctuations will be displayed as vertical
            # punctuations in vertical writing mode (but not vice versa),
            # so we'll just use horizontal ones.
            text = self.batch_replace(
                text=text,
                replacement_dict={
                    "﹁": "「",
                    "﹂": "」",
                    "﹃": "『",
                    "﹄": "』",
                },
            )
        if source_locale != target_locale:
            if source_locale == "hans":
                text = self.batch_replace(
                    text=text,
                    replacement_dict={
                        "‘": "「",
                        "’": "」",
                        "“": "『",
                        "”": "』",
                    },
                )

            # swap single quotes with double quotes
            text = self.batch_replace(
                text=text,
                replacement_dict={
                    "『": "「",
                    "』": "」",
                    "「": "『",
                    "」": "』",
                },
            )

            if target_locale == "hans" and horizontal:
                text = self.batch_replace(
                    text=text,
                    replacement_dict={
                        "「": "‘",
                        "」": "’",
                        "『": "“",
                        "』": "”",
                    },
                )

        return text

    def map_locale(self, x: str) -> Literal["hans", "hant"]:
        if x in ["s", "sp"]:
            return "hans"
        return "hant"

    def batch_replace(self, text: str, replacement_dict: Dict[str, str]) -> str:
        if len(replacement_dict) == 0:
            return text
        return re.sub(
            "|".join(re.escape(key) for key in replacement_dict.keys()),
            lambda k: replacement_dict[k.group(0)],
            text,
        )
