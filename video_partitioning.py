from math import floor
from typing import Callable

from faster_index import FasterIndex as Fi
from score_ordered_prefix_tree import ScoreOrderPrefixTree as Sopt
from utils import sort_all_objs_in_frames as sort_obj, add_id_for, Frame
from utils import build_pos_map as build_pm


class Partition:
    def __init__(self, pid: int, frames):
        self.id = pid
        self.obj_ids = sort_obj(frames)
        self.obj_pos_map = build_pm(self.obj_ids)
        self.frames = add_id_for(frames)
        # TODO(lu): maintain an index for each label
        self.index = None

    def build_index(self, obj_filter: Callable[[list], list]):
        """
        build index for a label
        :param obj_filter: the function the filter object according to the label
        :return: a list of frames containing passed-by objects
        """
        sopt_forest = Sopt()
        sopt_forest.build(obj_filter(self.frames))
        self.index = Fi(self.obj_ids, self.obj_pos_map)
        self.index.build(sopt_forest.trees)
        del sopt_forest

    def max_score(self):
        if self.index is None:
            raise ValueError("No index is built.")
        return self.index.sorted_nodes[-1]


class VideoPartition:
    def __init__(self, video_frames: list[Frame], partition_size: int):
        self.frames = video_frames
        self.part_size = partition_size
        self.partitions = []
        counter = 0
        for i in range(0, len(self.frames), partition_size):
            self.partitions.append(Partition(counter, self.frames[i:i + partition_size]))
            counter += 1

    def build_all_index(self, obj_filter: Callable[[list], list]):
        for portion in self.partitions:
            portion.build_index(obj_filter)


class PartitionGroup:
    def __init__(self, window_size: int, partition_size: int, group_size: int = None):
        self.size = group_size if group_size is not None else floor((window_size - 1) / partition_size)
