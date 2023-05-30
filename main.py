from frame_reader import DummyFrameReader as Dr
from query_processing import partition_based_query_processing as rwqr
from video_partitioning import VideoPartition

part_size = 3

frames = Dr().frame_list(False)
partition = VideoPartition(frames, part_size)
partition.build_hash_index()
fake_indexed_labels = {"car"}
fake_obj_labels = {i: {"car"} for i in range(1, 5)}
partition.build_labels_index(fake_indexed_labels, fake_obj_labels)

w_size = 4
pg_len = 6
k = 1
condition = {'car': 2}
res = rwqr(partition, w_size, pg_len, k, condition)

