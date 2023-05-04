from typing import Callable, Any, Iterable


def breath_first_search(roots, visit: Callable[[Any], None]) -> None:
    """ visit a tree via its root, and call `visit` function for all nodes, where
        `visit` take in a node as argument."""
    nodes_queue = [roots]
    while len(nodes_queue) != 0:
        node = nodes_queue.pop()
        visit(node)
        nodes_queue.extend(node.children)


class Object:
    def __init__(self, oid,  in_frames: list):
        self.id = oid
        self.my_frames = in_frames

    def score(self):
        return len(self.my_frames)


class Frame(list):
    def __init__(self, fid, object_ids):
        self.fid = fid
        super().__init__(object_ids)


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
                if object_map.get(obj_id) is None:
                    object_map[obj_id] = Object(obj_id, [frame.fid])
                else:
                    object_map[obj_id].my_frames.append(frame.fid)

        super().__init__(object_map)

    def most_common(self):
        return max(super().items(), key=lambda item: item[1].score())[1]
