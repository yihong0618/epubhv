import re


class Punctuation:
    V = {
        'hant': {
            'OPENING_QUOTE': '﹁',
            'CLOSING_QUOTE': '﹂',
            'OPENING_INNER_QUOTE': '﹃',
            'CLOSING_INNER_QUOTE': '﹄',
        },
        'hans': {
            'OPENING_QUOTE': '﹃',
            'CLOSING_QUOTE': '﹄',
            'OPENING_INNER_QUOTE': '﹁',
            'CLOSING_INNER_QUOTE': '﹂',
        }
    }
    H = {
        'hant': {
            'OPENING_QUOTE': '「',
            'CLOSING_QUOTE': '」',
            'OPENING_INNER_QUOTE': '『',
            'CLOSING_INNER_QUOTE': '』',
        },
        'hans': {
            'OPENING_QUOTE': '“',
            'CLOSING_QUOTE': '”',
            'OPENING_INNER_QUOTE': '‘',
            'CLOSING_INNER_QUOTE': '’',
        }
    }

    def convert(self, text, horizontal, source_locale, target_locale):
        replacement_dict = {}

        # convert between hant and hans
        if target_locale != source_locale:
            replacement_dict = {
                self.H[source_locale]['OPENING_QUOTE']: self.H[target_locale]['OPENING_QUOTE'],
                self.H[source_locale]['CLOSING_QUOTE']: self.H[target_locale]['CLOSING_QUOTE'],
                self.H[source_locale]['OPENING_INNER_QUOTE']: self.H[target_locale]['OPENING_INNER_QUOTE'],
                self.H[source_locale]['CLOSING_INNER_QUOTE']: self.H[target_locale]['CLOSING_INNER_QUOTE'],
            }

        if horizontal:
            replacement_dict.update({
                self.V[source_locale]['OPENING_QUOTE']: self.H[target_locale]['OPENING_QUOTE'],
                self.V[source_locale]['CLOSING_QUOTE']: self.H[target_locale]['CLOSING_QUOTE'],
                self.V[source_locale]['OPENING_INNER_QUOTE']: self.H[target_locale]['OPENING_INNER_QUOTE'],
                self.V[source_locale]['CLOSING_INNER_QUOTE']: self.H[target_locale]['CLOSING_INNER_QUOTE'],
            })
        else:
            # Horizontal punctuations will be displayed as vertical
            # punctuations in vertical writing mode (but not vice versa),
            # so we'll just use horizontal ones.
            pass

        return re.sub('|'.join(re.escape(key) for key in replacement_dict.keys()),
                      lambda k: replacement_dict[k.group(0)], text)

    def map_locale(self, x):
        if x in ['s', 'sp']:
            return 'hans'
        return 'hant'
