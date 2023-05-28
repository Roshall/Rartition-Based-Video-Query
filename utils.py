from itertools import chain
from typing import Callable, Any, Iterable

from bitmap import BitMap


def breath_first_search(roots, visit: Callable[[Any], None]) -> None:
    """ visit a tree via its root, and call `visit` function for all nodes, where
        `visit` take in a node as argument."""
    nodes_queue = [roots]
    while len(nodes_queue) != 0:
        node = nodes_queue.pop()
        visit(node)
        nodes_queue.extend(node.children)


def build_pos_map(obj_ids):
    obj_pos_map = {}
    for i, obj in enumerate(obj_ids):
        obj_pos_map[obj] = i
    return obj_pos_map


def add_id_for(frames, start_p):
    new_f = []
    for i, obj_id_list in enumerate(frames, start_p):
        new_f.append(Frame(i, obj_id_list))
    return new_f

def bitmap_of(obj_ids: Iterable, all_obj_num, obj_ids_map):
    bitmap = BitMap(all_obj_num)
    for oid in obj_ids:
        if oid in obj_ids_map:
            bitmap.set(obj_ids_map[oid])


class ObjectWithFrames:
    def __init__(self, oid, in_frames: list):
        self.id = oid
        self.my_frames = in_frames

    def score(self):
        return len(self.my_frames)


class Frame(list):
    """
    Basically a list of object ids, plus the id of the frame.
    """
    def __init__(self, fid, object_ids):
        self.fid = fid
        super().__init__(object_ids)


def sort_all_objs_in_frames(frames: list[Frame]):
    """
    sort all objects in frames and deduplicate object
    :param frames: frames
    :return: sorted distinct objects list
    """
    return sorted(set(chain(*frames)))


class ObjectCounter(dict):
    """
    essentially, This class stores all the frames that each object is in.
    and object's score is simply # of frames
    """

    def __init__(self, frames: Iterable = None):
        self.max = None
        object_map = {}
        for frame in frames:
            for obj_id in frame:
                if obj_id not in object_map:
                    object_map[obj_id] = ObjectWithFrames(obj_id, [frame.fid])
                else:
                    object_map[obj_id].my_frames.append(frame.fid)

        super().__init__(object_map)

    def most_common(self):
        return max(super().items(), key=lambda item: item[1].score())[1]


class Window:
    def __init__(self, interval=None):
        self.interval = interval
        self.score = 0 if interval is None else len(interval)

    def __lt__(self, other):
        return self.score < other.score
