# wikilink

find shortest hyperlink path over wikipedia pages

## usage

### cli

```sh
py main.py ./enwiki-latest-pages-articles.xml
```

### interpreter

```py
from main import *
graph = load_graph("enwiki-latest-pages-articles.xml")
```

```py
graph.find_path("source code", "philosophy")
```

---

[latest english wikipedia dump](https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2)
