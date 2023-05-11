from heapq import heappop, heappush, heapify, heapreplace

from utils import Window, bitmap_of
from video_partitioning import VideoPartition as Vp, PartitionGroup, Partition, Group


def evaluate(bitmap, condition, labels_index):
    for label in condition:
        if (bitmap & labels_index[label]).count() < condition[label]:
            return False
    return True


def update_res(res, w_size, obj_intervals, query_interval):
    start, end = query_interval
    for obj_i in obj_intervals:
        lower, upper = min(obj_intervals), max(obj_intervals)
        lower = max(start, lower - w_size + 1)
        upper = min(end, upper + w_size - 1)
        obi_i = set(obj_i)
        candidate = set(range(lower, min(lower + w_size, upper) + 1))
        candidate &= obj_i
        if len(candidate) > res[0].score:
            heapreplace(res, Window(list(candidate)))
        for anchor in range(lower + w_size + 1, upper + 1):
            candidate.discard(anchor - w_size)
            if anchor in obi_i:
                candidate.add(anchor)
            if len(candidate) > res[0].score:
                heapreplace(res, Window(list(candidate)))


def process_pg(group: Group[Partition], pause_score, res, condition, w_size):
    part_queue = group[:]
    heapify(part_queue)
    while (est_score := group.estimate_score()) >= pause_score and est_score >= res[0].score:
        partition = heappop(part_queue)
        node = partition.max_score_node()
        processed_bms = set()
        target_bm = node.bitmap
        if evaluate(target_bm, condition, partition.label_index):
            oid_seq = partition.whole_seq_of(target_bm)
            objs_to_intervals = {}
            for obj_id in oid_seq:  # TODO: check if obj_id's label fulfills conditions, even though paper doesn't say
                for obj_ids, intervals in group.get(obj_id, partition.id):
                    trans_bm = bitmap_of(obj_ids, len(partition.obj_ids), partition.obj_pos_map)
                    bmR = target_bm & trans_bm
                    if bmR not in group.processed_bms and evaluate(bmR, condition, partition.label_index):
                        if bmR in objs_to_intervals:
                            objs_to_intervals[bmR].extend(intervals)
                        else:
                            objs_to_intervals[bmR] = intervals[:]
                        processed_bms.add(bmR)
                update_res(res, w_size, objs_to_intervals, group.interval())
        partition.query_advance()
        group.processed_bms |= processed_bms
        heappush(part_queue, partition)


def coarse_filter(part, condition) -> bool:
    for label in condition:
        if part.num_objs_has_label(label) < condition[label]:
            return False
    return True


def partition_based_query_processing(partitions: Vp, w_size: int, pg_len: int, k: int, condition):
    """
    answer user query
    :param partitions: Video Partitions
    :param w_size: query window size
    :param k: return top k results
    :param condition: filter condition
    :param pg_len: # of partitions in each Partition Group
    :return: query result list
    """
    # 1. filter partition base on condition
    for part in partitions:
        if coarse_filter(part, condition):
            part.new_query()
        else:
            part.new_query(active=False)

    pg = PartitionGroup(partitions, w_size, partitions.part_size, pg_len)
    res = []
    for _ in range(k):
        heappush(res, Window())
    while (queue_max := pg.max_score()) >= (res_min := res[0].score) and queue_max > 0 and res_min < w_size:
        group = heappop(pg)
        pause_score = pg.max_score()
        process_pg(group, pause_score, res, condition, w_size)
        heappush(pg, group)
    return res
