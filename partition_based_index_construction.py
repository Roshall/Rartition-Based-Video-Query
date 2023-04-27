import collections
import copy


def count_map_construct(frames: list) -> collections.Counter:
    from itertools import chain
    from collections import Counter
    return Counter(chain(*frames))


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
    new_list = []
    for fr in frames:
        if obj in fr:
            fr.remove(obj)
            new_list.append(fr)
    return new_list


def update_state(count_map: collections.Counter, frames):
    entry = count_map.most_common(1)[0]
    obj, count = entry
    del count_map[obj]
    node = Node(obj, count)
    filtered_frames = filter_by_obj(frames, obj)
    return node, filtered_frames, entry


def del_from_count_maps(all_count_map, entry):
    obj, count = entry
    for cmap in all_count_map:
        if cmap.get(obj) == count:
            del cmap[obj]


def build_next(p_node, all_count_map, frames):
    my_count_map = count_map_construct(frames)
    all_count_map.append(my_count_map)
    while len(my_count_map) > 0:
        node, filter_frames, entry = update_state(my_count_map, frames)
        p_node.add_child(node)
        del_from_count_maps(all_count_map, entry)
        build_next(node, all_count_map, filter_frames)
    all_count_map.pop()


def partition_based_index_construction(frames: list) -> list:
    frames = copy.deepcopy(frames)  # we will modify it so copy it
    forest_roots = []
    count_map = count_map_construct(frames)
    all_count_map = [count_map]
    while len(count_map) > 0:
        node, filtered_frames, _ = update_state(count_map, frames)
        build_next(node, all_count_map, filtered_frames)
        forest_roots.append(node)
        count_map = count_map_construct(frames)  # this line is different from the paper
    return forest_roots
