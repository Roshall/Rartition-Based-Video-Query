import frame_reader
import score_ordered_prefix_tree as sopt


class TestSopt:
    def test_build(self):
        frames = frame_reader.DummyFrameReader().frame_list()
        tree_index = sopt.ScoreOrderPrefixTree(frames)
        tree_index.print()
