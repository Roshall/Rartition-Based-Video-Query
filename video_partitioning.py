import heapq
from itertools import chain
from math import floor
from typing import Callable, Iterable

from bitmap import BitMap
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
        self.condition_filter = None
        self.query_pointer = None

    def build_index(self, label_filter: Callable[[list], list]):
        """
        build index for a label
        :param label_filter: filter function that filters objects according to the label
        :return: a list of frames containing passed-by objects
        """
        sopt_forest = Sopt(label_filter(self.frames))
        self.index = Fi(self.obj_ids, self.obj_pos_map, sopt_forest.trees)
        del sopt_forest

    def get(self, obj_id):
        node = self.index.get(obj_id)
        if node is not None:
            return self.whole_seq_of(node.bitmap), node.my_frames
        else:
            return None

    def max_score_node(self):
        # TODO(lu): support condition filter
        if self.index is None or self.query_pointer is None:
            raise ValueError("No index is built or no current query.")
        res = None
        for i in range(self.query_pointer, -1, -1):
            if node := self.condition_filter(self.index.sorted_nodes[i]):
                res = node
                break
        return res

    def max_score(self):
        node = self.max_score_node()
        return node.score if node is not None else 0

    def whole_seq_of(self, node):
        """
        get the whole sequence respect to its bitmap
        :param node:  a node
        :return: seq generator
        """
        for pos in node.bitmap.nonzero():
            yield self.obj_ids[pos]

    def new_query(self, condition_filter):
        self.query_pointer = len(self.obj_ids) - 1
        self.condition_filter = condition_filter

    def __lt__(self, other):
        """
        support max heap for build-in heapq.
        """
        return self.max_score() > other.max_score()

    def __eq__(self, other):
        return self.max_score() == other.max_score()


class VideoPartition(list):
    def __init__(self, video_frames: list[Frame], partition_size: int):
        self.frames = video_frames
        self.part_size = partition_size
        super().__init__()
        partitions = super()
        counter = 0
        for i in range(0, len(self.frames), partition_size):
            partitions.append(Partition(counter, self.frames[i:i + partition_size]))
            counter += 1

    def build_index(self, label_filter: Callable[[list], list]):
        for portion in super():
            portion.build_index(label_filter)


class Group(list):
    def __init__(self, gid: int, partitions: list[Partition], w_size):
        super().__init__(partitions)
        self.id = gid
        self.w_size = w_size
        self.est_score = None
        self.obj_ids = set(chain(part.obj_ids for part in partitions))
        self.obj_ids_map = {val: i for i, val in enumerate(self.obj_ids)}
        self.processed_bms = set()

    def estimate_score(self, reset=False):
        if reset or self.est_score is None:
            partitions = super()
            windows_max_score = []
            for i in range(0, len(partitions)-self.w_size, self.w_size):
                # TODO(lu): try to use generator instead of list
                windows_max_score.append(sum(map(lambda p: p.max_score(), partitions[i:i+self.w_size])))
            self.est_score = max(windows_max_score)

        return self.est_score

    def get(self, obj_id, exclude_partition):
        """
        get all nodes contains obj
        :param exclude_partition: skip this partition
        :param obj_id:
        :return: generator of desiderata: tuple of (obj_ids, interval)
        """
        for part in super():
            if part.id != exclude_partition:
                yield (obj for obj in part.get(obj_id) if obj is not None)

    def bitmap_of(self, obj_ids: Iterable):
        bitmap = BitMap(len(self.obj_ids))
        for oid in obj_ids:
            pos = self.obj_ids_map[oid]
            bitmap.set(pos)
        return bitmap

    def __lt__(self, other):
        """
        support max heap for build-in heapq.
        """
        return self.estimate_score() > other.estimate_score()

    def __eq__(self, other):
        return self.estimate_score() > other.estimate_score()


class PartitionGroup(list):
    """
    This class is instantiated only for a query
    """
    def __init__(self, partitions: list[Partition], window_size: int, partition_size: int, group_len: int):
        """
        After init, a priority queue will be built.
        :param partitions: a list of partitions
        :param window_size:
        :param partition_size:
        :param group_len: set to -1 if not concern
        """
        self.Vparts = partitions
        # 1. build partition group
        minimal_size = floor((window_size - 1) / partition_size)
        self.size = group_len if group_len > minimal_size else minimal_size
        super().__init__()
        groups = super()
        counter = 0
        # the stride is (pg -upper_bound + 1), which is also # of distinct windows a group encloses
        # Therefore, the whole groups list guarantees that all windows will be covered
        for i in range(0, len(self.Vparts), self.size - minimal_size + 1):
            groups.append(Group(counter, self.Vparts[i:i + self.size], window_size))
        # 2. build priority_queue
        heapq.heapify(groups)

    def max_score(self):
        return super()[0].estimate_score()
