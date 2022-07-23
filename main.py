from collections import deque
import xml.etree.ElementTree as ET
import sys
import re
import pickle
from os import path


class Graph(object):

    def __init__(self):
        self._dict = dict()

    def add(self, origin, destinations):
        origin = origin.lower()

        if not origin in self._dict:
            self._dict[origin] = set()

        for dest in destinations:
            self._dict[origin].add(dest.lower())

    def find_path(self, origin, destination):
        origin = origin.lower()
        destination = destination.lower()

        visited = set([origin])
        queue = deque()
        queue.append(origin)
        through = {origin: None}

        while queue:
            current = queue.popleft()

            if not current in self._dict:
                continue

            for node in self._dict[current]:
                if not node in visited:
                    visited.add(node)
                    queue.append(node)
                    through[node] = current

                    if node == destination:
                        queue.clear()
                        break

        if not destination in through:
            return None

        path = [destination]
        while path[-1] != origin:
            path.append(through[path[-1]])

        path.reverse()

        return path

    def optimize(self):
        self._dict.update(self._dict)


def parse_links(wikitext):
    if not type(wikitext) == str:
        return []

    return re.findall("\[\[(.+?)[\|\]]", wikitext)


def parse_xml(xmlfile):
    # TODO remove standalone redirect nodes

    graph = Graph()

    path = []
    title = ""
    page_count = 0
    for event, elem in ET.iterparse(xmlfile, events=("start", "end")):
        _, has_namespace, postfix = elem.tag.partition("}")
        if has_namespace:
            elem.tag = postfix

        if event == "start":
            path.append(elem.tag)
        elif event == "end" and "page" in path:
            if elem.tag == "title":
                title = elem.text
            elif elem.tag == "text":
                graph.add(title, parse_links(elem.text))
                page_count += 1
                if page_count % 10000 == 0:
                    print(f"parsed {page_count / 1000}K pages")
            elif elem.tag == "redirect":
                graph.add(title, [elem.attrib["title"]])
            path.pop()

    graph.optimize()

    return graph


def load_graph(wikidump):
    cache_file = f"{wikidump}.cache"

    if path.exists(cache_file):
        print("found cached graph")
        with open(cache_file, "rb") as f:
            graph = pickle.load(f)
        print("loaded cache")
    else:
        print(f"parsing {wikidump}")
        graph = parse_xml(wikidump)
        with open(cache_file, "wb") as f:
            pickle.dump(graph, f)
        print("parsing done and cached")

    return graph


def main():
    args = sys.argv[1:]
    file = args[0]

    graph = load_graph(file)

    print(graph.find_path("leonardo da vinci", "coffee"))


if __name__ == "__main__":
    main()
