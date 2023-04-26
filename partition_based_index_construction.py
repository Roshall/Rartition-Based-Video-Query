import collections


def count_map_construct(frames: list) -> collections.Counter:
    from itertools import chain
    from collections import Counter
    return Counter(chain(*frames))


def compute_score(objs) -> int:
    return objs[-1][-1]


class Node:
    def __init__(self, obj, score):
        self.obj = obj
        self.score = score
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __eq__(self, other):
        return self.obj == other.obj and self.score == other.score and self.children == other.children


def filter_by_obj(frames, obj):
    return [f for f in frames if obj in f]


def update_state(count_map: collections.Counter, objs, frames):
    entry = count_map.most_common(1)[0]
    del count_map[entry[0]]
    objs.append(entry)
    score = compute_score(objs)
    node = Node(entry[0], score)
    filtered_frames = filter_by_obj(frames, entry[0])
    return node, filtered_frames, entry


def del_from_count_maps(all_count_map, entry):
    for cmap in all_count_map:
        if cmap.get(entry[0]) == entry[1]:
            del cmap[entry[0]]


def build_next(p_node, all_count_map, frames, objs):
    my_count_map = count_map_construct(frames)
    all_count_map.append(my_count_map)
    while len(my_count_map) > 0:
        node, filter_frames, entry = update_state(my_count_map, objs, frames)
        p_node.add_child(node)
        del_from_count_maps(all_count_map, entry)
        build_next(node, all_count_map, filter_frames, objs)
    all_count_map.pop()


def partition_based_index_construction(frames: list) -> list:
    forest_roots = []
    count_map = count_map_construct(frames)
    all_count_map = [count_map]
    objs = []
    while len(count_map) > 0:
        node, filtered_frames, _ = update_state(count_map, objs, frames)
        build_next(node, all_count_map, filtered_frames, objs)
        objs.pop()
        forest_roots.append(node)
    return forest_roots
