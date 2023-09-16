import re


class Punctuation:
    def convert(self, text, horizontal, source_locale, target_locale):
        if horizontal:
            # Horizontal punctuations will be displayed as vertical
            # punctuations in vertical writing mode (but not vice versa),
            # so we'll just use horizontal ones.
            text = self.batch_replace(
                text,
                {
                    "﹁": "「",
                    "﹂": "」",
                    "﹃": "『",
                    "﹄": "』",
                },
            )
        if source_locale != target_locale:
            if source_locale == "hans":
                text = self.batch_replace(
                    text,
                    {
                        "‘": "「",
                        "’": "」",
                        "“": "『",
                        "”": "』",
                    },
                )

            # swap single quotes with double quotes
            text = self.batch_replace(
                text,
                {
                    "『": "「",
                    "』": "」",
                    "「": "『",
                    "」": "』",
                },
            )

            if target_locale == "hans" and horizontal:
                text = self.batch_replace(
                    text,
                    {
                        "「": "‘",
                        "」": "’",
                        "『": "“",
                        "』": "”",
                    },
                )

        return text

    def map_locale(self, x):
        if x in ["s", "sp"]:
            return "hans"
        return "hant"

    def batch_replace(self, text: str, replacement_dict: dict):
        if len(replacement_dict) == 0:
            return text
        return re.sub(
            "|".join(re.escape(key) for key in replacement_dict.keys()),
            lambda k: replacement_dict[k.group(0)],
            text,
        )
