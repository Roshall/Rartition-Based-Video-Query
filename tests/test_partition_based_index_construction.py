import frame_reader
import partition_based_index_construction as pbic


class TestTPBIC:
    frames = frame_reader.DummyFrameReader().frame_list()

    def test_count_map_construct(self):
        count_map = pbic.count_map_construct(self.frames)
        assert len(count_map) != 0
        ans = {1: 2, 2: 2, 3: 3}
        assert count_map == ans

    def test_filter_by_obj(self):
        res = [[1, 3], [1, 2, 3]]
        assert pbic.filter_by_obj(self.frames, 1)

    def test_update_state(self):
        count_map = pbic.count_map_construct(self.frames)
        objs = [(4, 4)]
        correct_ans = pbic.Node(3, 3), [[2, 3], [1,3], [1, 2, 3]], (3, 3)
        assert pbic.update_state(count_map, objs, self.frames) == correct_ans

    def test_partition_based_index_construction(self):
        roots = pbic.partition_based_index_construction(self.frames)
        assert len(roots) != 0
        assert roots[0].id == 1
