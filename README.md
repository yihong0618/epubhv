# epubhv

make your epub books vertical or horizontal.

## You can use [streamlit](https://epubhv.streamlit.app)

## Install

```
pip install epubhv
or
git clone https://github.com/yihong0618/epubhv.git
cd epubhv && bash ./setup.sh
```

## Using pipx

If you are using [pipx](https://pypi.org/project/pipx/), you can directly run `epubhv` with:

```console
pipx run epubhv a.epub
```

## Use the web

```console
pip install epubhv[web]
streamlit run web.py
```

## Use CLI

```console
epubhv a.epub # will generate a file a-v.epub that is vertical
# or
epubhv b.epub --h # will generate a file b-h.epub that is horizontal

# if you also want to translate from `简体 -> 繁体`
epubhv c.epub --convert s2t

# if you also want to translate from `繁体 -> 简体`
epubhv d.epub --h --convert t2s

# or a folder contains butch of epubs
epubhv tests/test_epub # will generate all epub files to epub-v

# you can specify the punctuation style
epubhv e.epub --convert s2t --punctuation auto
# you can add `ruby` for Japanese(furigana) and Chinese(pinyin)
epubhv e.epub --h --ruby
# if you want to learn `cantonese` 粤语
epubhv f.epub --h --ruby --cantonese
```

**About [cantonese](https://jyutping.org/docs/cantonese/)**

## Contribution

- Any issues or PRs are welcome.

## Development

```console
# install all dependencies
pdm install

# format code
pdm run format

# run the following scripts and make sure all pass before you start a Pull Request
pdm run all
```

## Thanks

- @[tommyku](https://github.com/tommyku) --> [How to make EPUB ebooks with vertical layout?](https://blog.tommyku.com/blog/how-to-make-epubs-with-vertical-layout/)
- @[jiak94](https://github.com/jiak94) support OpenCC
- @[OverflowCat ](https://github.com/OverflowCat) add punctuation styles.
- @[jt-wang](https://github.com/jt-wang) Type and PDM!
- [furigana4epub](https://github.com/Mumumu4/furigana4epub)
- [ToJyutping](https://github.com/CanCLID/ToJyutping)
- [PDM](https://pdm.fming.dev/latest/)
- [Streamlit](https://streamlit.io/)

## Similar projects

- [EpubConv_Python](https://github.com/ThanatosDi/EpubConv_Python) found a similar project, seems we are not the only one need this, great thanks, appreciation and respect.

## Appreciation

- Thank you, that's enough. Just enjoy it.

![image](https://github.com/yihong0618/epubhv/assets/15976103/6c6d77fc-6d3c-4814-b37c-badeba38cd03)
![image](https://github.com/yihong0618/epubhv/assets/15976103/d8526e7c-abd2-42e2-92c8-d32300cec343)
![image](https://github.com/yihong0618/epubhv/assets/15976103/685b789f-1850-43ed-b695-a70f86ec7dd0)
