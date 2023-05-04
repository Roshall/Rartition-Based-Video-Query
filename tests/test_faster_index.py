from frame_reader import DummyFrameReader as Dr
from score_ordered_prefix_tree import ScoreOrderPrefixTree as Sopt
from faster_index import FasterIndex


class TestFastIndex:
    def test_build_faster_index(self):
        frames = Dr().frame_list()
        sopt_forest = Sopt()
        sopt_forest.build(frames)
        trees = sopt_forest.trees
        fi = FasterIndex(sopt_forest.obj_ids)
        fi.build(trees)
        for obj_id, members in fi.obj_map.items():
            print(obj_id)
            for item in members:
                print(item.obj.bitmap, item.obj.my_frames, end=' ;')
            print()
