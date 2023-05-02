from frame_reader import DummyFrameReader as Dr
from score_ordered_prefix_tree import ScoreOrderPrefixTree as Sopt
from faster_index import FasterIndex


class TestFastIndex:
    def test_build_faster_index(self):
        frames = Dr().frame_list()
        sopt_forest = Sopt()
        sopt_forest.build(frames)
        trees = sopt_forest.trees
        fi = FasterIndex(sopt_forest.objs)
        fi.build(trees)
        for obj, members in fi.obj_map.items():
            print(obj, members[0], end=": ")
            for item in members[1:]:
                print(obj, item, end=' ;')
            print()
