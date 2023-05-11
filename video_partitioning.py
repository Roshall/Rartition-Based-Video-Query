import heapq
from itertools import chain
from math import floor

from bitmap import BitMap
from faster_index import FasterIndex as Fi
from score_ordered_prefix_tree import ScoreOrderPrefixTree as Sopt
from utils import sort_all_objs_in_frames as sort_obj, add_id_for, Frame
from utils import build_pos_map as build_pm


class Partition:
    def __init__(self, pid: int, frames, start_p, end_p):
        self.id = pid
        self.obj_ids = sort_obj(frames)
        self.obj_pos_map = build_pm(self.obj_ids)
        self.interval = start_p, end_p
        self.frames = add_id_for(frames, start_p)
        self.hash_index = None
        self.label_index = None
        self.query_pointer = -1

    def build_fast_index(self):
        """
        build index for a label
        :return: a list of frames containing passed-by objects
        """
        sopt_forest = Sopt(self.frames)
        self.hash_index = Fi(self.obj_ids, self.obj_pos_map, sopt_forest.trees)
        del sopt_forest

    def build_labels_index(self, indexed_labels, obj_labels):
        bm_bit = len(self.obj_ids)
        label_index = {indexed_l: BitMap(bm_bit) for indexed_l in indexed_labels}
        for obj_id in self.obj_ids:
            labels = obj_labels[obj_id] & indexed_labels
            for label in labels:
                label_index[label].set(self.obj_pos_map[obj_id])
        self.label_index = label_index

    def get(self, obj_id):
        return self.hash_index.get(obj_id)

    def max_score_node(self):
        res = None
        if self.query_pointer >= 0:
            res = self.hash_index.sorted_node[self.query_pointer]
        return res

    def max_score(self):
        node = self.max_score_node()
        return node.score if node is not None else 0

    def whole_seq_of(self, bitmap):
        """
        get the whole sequence respect to its bitmap
        :param bitmap:  a bitmap
        :return: seq generator
        """
        for pos in bitmap.nonzero():
            yield self.obj_ids[pos]

    def num_objs_has_label(self, label) -> int:
        if label in self.label_index:
            return self.label_index[label].count()
        else:
            return 0

    def new_query(self, active=True):
        if active:
            self.query_pointer = len(self.obj_ids) - 1
        else:
            self.query_pointer = -1

    def query_advance(self):
        """
        only after calling this func, one can query next node
        :return: None
        """
        self.query_pointer -= 1

    def interval(self):
        return self.interval

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
            partitions.append(Partition(counter, (f for f in self.frames[i:i + partition_size]), i, i+partition_size-1))
            counter += 1

    def build_hash_index(self):
        for portion in super():
            portion.build_fast_index()

    def build_label_index(self, indexed_labels, obj_labels):
        for portion in super():
            portion.build_label_index(indexed_labels, obj_labels)


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
                # FIXME(lu): not max_score, but max estimate score (according to the paper),
                #  which take condition into consideration
                #  albeit, maybe it is the right way to just return max_score
                windows_max_score.append(sum(map(lambda p: p.max_score(), (p for p in partitions[i:i+self.w_size]))))
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

    def interval(self):
        partitions = super()
        return partitions[0].interval()[0], partitions[-1].interval()[-1]

    def __lt__(self, other):
        """
        support max heap for build-in heapq.
        """
        return self.estimate_score() > other.estimate_score()

    def __eq__(self, other):
        return self.estimate_score() == other.estimate_score()


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
