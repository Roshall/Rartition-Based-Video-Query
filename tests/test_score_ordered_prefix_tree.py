import frame_reader
import score_ordered_prefix_tree as sopt
from utils import Frame


def print_tree(root, level: int = 0) -> None:
    print("--" * level, root.obj.id, root.obj.my_frames)
    for child in root.children:
        print_tree(child, level + 1)


def print_forest(roots: list) -> None:
    for tree in roots:
        print()
        print_tree(tree)


class TestSopt:
    def test_build(self):
        frames = frame_reader.DummyFrameReader().frame_list()
        tree_index = sopt.ScoreOrderPrefixTree()
        tree_index.build(frames)
        trees = tree_index.trees
        assert len(trees) > 0
        print_forest(trees)
