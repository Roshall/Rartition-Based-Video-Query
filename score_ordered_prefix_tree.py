import copy
from typing import Iterable

from utils import ObjectCounter


class Node:
    def __init__(self, obj):
        self.obj = obj
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __eq__(self, other):
        return self.obj == other.obj and self.children == other.children


def filter_by_obj(frames: Iterable, obj_id):
    new_list = []
    for fr in frames:
        if obj_id in fr:
            fr.remove(obj_id)
            new_list.append(fr)
    return new_list


def update_state(count_map: ObjectCounter, frames):
    obj = count_map.most_common()
    oid = obj.id
    del count_map[oid]
    node = Node(obj)
    filtered_frames = filter_by_obj(frames, oid)
    return node, filtered_frames, obj


class ScoreOrderPrefixTree:
    def __init__(self):
        self.obj_ids = []
        self.trees = []
        self.all_count_map = []

    def __count_maps_del(self, entry):
        target_id = entry.id
        for cmap in self.all_count_map:
            if (obj := cmap.get(target_id)) is not None and obj.score() == entry.score():
                del cmap[target_id]

    def __build_next(self, p_node, frames):
        my_count_map = ObjectCounter(frames)
        self.all_count_map.append(my_count_map)
        while len(my_count_map) > 0:
            node, filter_frames, entry = update_state(my_count_map, frames)
            p_node.add_child(node)
            self.__count_maps_del(entry)
            self.__build_next(node, filter_frames)
        self.all_count_map.pop()

    def build(self, frames: list):
        frames = copy.deepcopy(frames)  # since we will modify it later
        count_map = ObjectCounter(frames)
        self.obj_ids.extend(sorted(count_map.keys()))
        self.all_count_map.append(count_map)
        while len(count_map) > 0:
            node, filtered_frames, _ = update_state(count_map, frames)
            self.__build_next(node, filtered_frames)
            self.trees.append(node)
            count_map = ObjectCounter(frames)  # this line is different from the paper
