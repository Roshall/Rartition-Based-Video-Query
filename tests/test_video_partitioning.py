from video_partitioning import Partition
from frame_reader import DummyFrameReader as Dr


class TestPartition:
    def test_build_fast_index(self):
        frames = Dr().frame_list(False)
        part = Partition(1, frames, 0, 7)
        part.build_fast_index()
        fake_indexed_labels = set("car")
        fake_obj_labels = {i: "car" for i in range(1, 5)}
        part.build_labels_index(fake_indexed_labels, fake_obj_labels)
        print(part)