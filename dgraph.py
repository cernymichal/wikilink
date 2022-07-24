from __future__ import annotations
from collections import deque
import pickle
from typing import TypeVar, Generic

T = TypeVar("T")


class DGraph(Generic[T]):

    def __init__(self):
        self._dict = dict[T, list[T]]()

    def add(self, origin: T, destinations: list[T]):
        if origin not in self._dict:
            self._dict[origin] = list[T]()

        self._dict[origin] = list(set(self._dict[origin]) | set(destinations))

    def find_path(self, origin: T, destination: T) -> list[T]:
        if origin not in self._dict or destination not in self._dict:
            return None

        visited = set([origin])
        queue = deque()
        queue.append(origin)
        through = {origin: None}

        while queue:
            current = queue.popleft()

            if current not in self._dict:
                continue

            for node in self._dict[current]:
                if node not in visited:
                    visited.add(node)
                    queue.append(node)
                    through[node] = current

                    if node == destination:
                        queue.clear()
                        break

        if destination not in through:
            return None

        path = [destination]
        while path[-1] != origin:
            path.append(through[path[-1]])

        path.reverse()

        return path

    def optimize(self):
        self._dict.update(self._dict)

    def pickle_dump(self, file: str):
        with open(file, "wb") as f:
            pickle.dump(self._dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def pickle_load(file: str) -> DGraph[T]:
        graph = DGraph[T]()
        with open(file, "rb") as f:
            graph._dict = pickle.load(f)

        return graph
