# epubhv

make your epub books vertical or horizontal.

## Install

```
pip install epubhv
or
git clone https://github.com/yihong0618/epubhv.git
cd epubhv && pip install .
```

## Use

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

```

## Thanks

- @[tommyku](https://github.com/tommyku) --> [How to make EPUB ebooks with vertical layout?](https://blog.tommyku.com/blog/how-to-make-epubs-with-vertical-layout/)
- @[jiak94](https://github.com/jiak94) support OpenCC

## Appreciation

- Thank you, that's enough. Just enjoy it.

![image](https://github.com/yihong0618/epubhv/assets/15976103/6c6d77fc-6d3c-4814-b37c-badeba38cd03)
![image](https://github.com/yihong0618/epubhv/assets/15976103/d8526e7c-abd2-42e2-92c8-d32300cec343)
