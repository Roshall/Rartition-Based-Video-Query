from collections import Counter
from typing import Callable
from itertools import chain


def breath_first_search(roots, visit: Callable) -> None:
    visit(roots)
    nodes_queue = []
    nodes_queue.extend(roots.children)
    while len(nodes_queue) != 0:
        node = nodes_queue.pop()
        visit(node)
        nodes_queue.extend(node.children)


def flatten_and_count(frames: list) -> Counter:
    return Counter(chain(*frames))