from __future__ import annotations
import xml.etree.ElementTree as ET
import sys
import re
import pickle
from os import path
from dgraph import DGraph


class WikipediaGraph(DGraph[str]):

    def __init__(self):
        super().__init__()
        self._aliases = dict[str, str]()

    def add(self, origin: str, destinations: list[str]):
        return super().add(origin.lower(), [i.lower() for i in destinations])

    def add_alias(self, alias: str, orig: str):
        self._aliases[alias.lower()] = orig.lower()

    def find_path(self, origin: str, destination: str) -> list[str]:
        origin = origin.lower()
        destination = destination.lower()

        if origin in self._aliases:
            origin = self._aliases[origin]

        if destination in self._aliases:
            destination = self._aliases[destination]

        return super().find_path(origin, destination)

    def optimize(self):
        super().optimize()
        self._aliases.update(self._aliases)

    def replace_aliases(self):
        # TODO pages missing (?)
        #for alias in self._aliases.keys():
        #    self._dict.pop(alias, None)

        for _, links in self._dict.items():
            for i, link in enumerate(links):
                if link in self._aliases:
                    links[i] = self._aliases[link]

    def pickle_dump(self, file: str):
        with open(file, "wb") as f:
            pickle.dump((self._dict, self._aliases),
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def pickle_load(file: str) -> WikipediaGraph:
        graph = WikipediaGraph()
        with open(file, "rb") as f:
            graph._dict, graph._aliases = pickle.load(f)

        return graph


def parse_links(wikitext) -> list[str]:
    if not type(wikitext) == str:
        return []

    return re.findall("\[\[(.+?)[\|\]]", wikitext)


def parse_xml(xmlfile: str):
    graph = WikipediaGraph()

    page_count = 0
    path = list[str]()
    title = ""
    redirect = False  # TODO pages missing (?)
    for event, elem in ET.iterparse(xmlfile, events=("start", "end")):
        _, has_namespace, postfix = elem.tag.partition("}")
        if has_namespace:
            elem.tag = postfix

        if event == "start":
            path.append(elem.tag)
        elif event == "end":
            if elem.tag == "page":
                redirect = False
                page_count += 1
                if page_count % 10000 == 0:
                    print(f"parsed {page_count / 1000}K pages")
            elif "page" in path:
                if elem.tag == "title":
                    title = elem.text
                elif elem.tag == "redirect":
                    graph.add_alias(title, elem.attrib["title"])
                    redirect = True
                elif elem.tag == "text":  #and not redirect:
                    graph.add(title, parse_links(elem.text))

            path.pop()

    graph.replace_aliases()
    graph.optimize()

    return graph


def load_graph(wikidump: str) -> WikipediaGraph:
    cache_file = f"{wikidump}.cache"

    if path.exists(cache_file):
        print("found cached graph")
        graph = WikipediaGraph.pickle_load(cache_file)
        print("loaded cache")
    else:
        print(f"parsing {wikidump}")
        graph = parse_xml(wikidump)
        graph.pickle_dump(cache_file)
        print("parsing done and cached")

    return graph


def main():
    args = sys.argv[1:]
    file = args[0]

    graph = load_graph(file)

    print(graph.find_path("leonardo da vinci", "coffee"))


if __name__ == "__main__":
    main()
