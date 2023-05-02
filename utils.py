from collections import Counter
from typing import Callable, Any
from itertools import chain


def breath_first_search(roots, visit: Callable[[Any], None]) -> None:
    """ visit a tree via its root, and call `visit` function for all nodes, where
        `visit` take in a node as argument."""
    nodes_queue = [roots]
    while len(nodes_queue) != 0:
        node = nodes_queue.pop()
        visit(node)
        nodes_queue.extend(node.children)


def flatten_and_count(frames: list) -> Counter:
    return Counter(chain(*frames))
