from frame_reader import DummyFrameReader as Dr
from score_ordered_prefix_tree import ScoreOrderPrefixTree as Sopt
from faster_index import FasterIndex
from utils import sort_all_objs_in_frames, build_pos_map


class TestFastIndex:
    def test_build_faster_index(self):
        frames = Dr().frame_list()
        obj_ids = sort_all_objs_in_frames(frames)
        pos_map = build_pos_map(obj_ids)
        sopt_forest = Sopt()
        sopt_forest.build(frames)
        trees = sopt_forest.trees
        fi = FasterIndex(obj_ids, pos_map)
        fi.build(trees)
        for obj_id, members in fi.obj_map.items():
            print(obj_id)
            for item in members:
                print(item.obj.bitmap, item.obj.my_frames, end=' ;')
            print()
