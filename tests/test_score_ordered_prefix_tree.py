import frame_reader
import score_ordered_prefix_tree as sopt


def print_tree(root, level: int = 0) -> None:
    print("--" * level, root.obj)
    for child in root.children:
        print_tree(child, level + 1)


def print_forest(roots: list) -> None:
    for tree in roots:
        print()
        print_tree(tree)


class TestTPBIC:
    frames = frame_reader.DummyFrameReader().frame_list()

    def test_partition_based_index_construction(self):
        self.frames.extend([[1, 4], [3], [3], [2, 4], [1, 2, 4]])
        tree_index = sopt.ScoreOrderPrefixTree()
        tree_index.construct(self.frames)
        trees = tree_index.trees
        assert len(trees) > 0
        print_forest(trees)
