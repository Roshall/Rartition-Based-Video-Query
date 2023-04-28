import copy
from collections import Counter
from utils import flatten_and_count


class Node:
    def __init__(self, obj, score):
        self.obj = obj
        self.score = score
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __eq__(self, other):
        return self.obj == other.obj and self.score == other.score and self.children == other.children


def filter_by_obj(frames: list, obj):
    new_list = []
    for fr in frames:
        if obj in fr:
            fr.remove(obj)
            new_list.append(fr)
    return new_list


def update_state(count_map: Counter, frames):
    entry = count_map.most_common(1)[0]
    obj, count = entry
    del count_map[obj]
    node = Node(obj, count)
    filtered_frames = filter_by_obj(frames, obj)
    return node, filtered_frames, entry


class ScoreOrderPrefixTree:
    def __init__(self):
        self.objs = []
        self.trees = []
        self.all_count_map = []

    def __count_maps_del(self, entry):
        obj, count = entry
        for cmap in self.all_count_map:
            if cmap.get(obj) == count:
                del cmap[obj]

    def __build_next(self, p_node, frames):
        my_count_map = flatten_and_count(frames)
        self.all_count_map.append(my_count_map)
        while len(my_count_map) > 0:
            node, filter_frames, entry = update_state(my_count_map, frames)
            p_node.add_child(node)
            self.__count_maps_del(entry)
            self.__build_next(node, filter_frames)
        self.all_count_map.pop()

    def construct(self, frames: list):
        frames = copy.deepcopy(frames)  # since we will modify it later
        count_map = flatten_and_count(frames)
        self.objs.extend(count_map.keys())
        self.all_count_map.append(count_map)
        while len(count_map) > 0:
            node, filtered_frames, _ = update_state(count_map, frames)
            self.__build_next(node, filtered_frames)
            self.trees.append(node)
            count_map = flatten_and_count(frames)  # this line is different from the paper
