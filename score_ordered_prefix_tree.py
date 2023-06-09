from typing import Iterable

from utils import ObjectCounter


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
    node = ScoreOrderPrefixTree.Node(obj)
    filtered_frames = filter_by_obj(frames, oid)
    return node, filtered_frames


def print_tree(root, level: int = 0) -> None:
    print("--" * level, root.obj.id, root.obj.my_frames)
    for child in root.children:
        print_tree(child, level + 1)


def print_forest(roots: list) -> None:
    for tree in roots:
        print()
        print_tree(tree)


class ScoreOrderPrefixTree:
    class Node:
        def __init__(self, obj):
            self.obj = obj
            self.children = []

        def add_child(self, node):
            self.children.append(node)

        def score(self):
            return self.obj.score()

    def __init__(self, frames: Iterable):
        self.trees = []
        self.all_count_map = []
        self.__build(frames)

    def __count_maps_del(self, entry):
        target_id = entry.obj.id
        for cmap in self.all_count_map:
            if (obj := cmap.get(target_id)) is not None and obj.score() == entry.score():
                del cmap[target_id]

    def __build_next(self, p_node, frames):
        my_count_map = ObjectCounter(frames)
        self.all_count_map.append(my_count_map)
        while len(my_count_map) > 0:
            node, filter_frames = update_state(my_count_map, frames)
            p_node.add_child(node)
            self.__count_maps_del(node)
            self.__build_next(node, filter_frames)
        self.all_count_map.pop()

    def __build(self, frames: Iterable):
        """
        build all sore order prefix trees for a list of frames
        :param frames: Iterable object that contains all the frames
        :return: None
        """
        frames = list(frames)
        count_map = ObjectCounter(frames)
        self.all_count_map.append(count_map)
        while len(count_map) > 0:
            node, filtered_frames = update_state(count_map, frames)
            self.__build_next(node, filtered_frames)
            self.trees.append(node)
            count_map = ObjectCounter(frames)  # this line is different from the paper

    def print(self):
        print_forest(self.trees)
