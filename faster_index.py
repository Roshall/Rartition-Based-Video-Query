from bitmap import BitMap
from utils import breath_first_search as bfs


class FasterIndex:
    def __init__(self, objs: list):
        self.maximum_bits = len(objs)
        self.obj_map = {}
        for i, obj in enumerate(objs):
            # 0-th: pos in bitmap
            # o/w: nodes
            self.obj_map[obj] = [i]

    def build_faster_index(self, sopt_forest: list):
        """ using hash and bitmap"""
        for tree in sopt_forest:
            tree.bitmap = BitMap(self.maximum_bits)
            bfs(tree, self.__visit_node)

    def __visit_node(self, node):
        pos = self.obj_map[node.obj][0]
        node.bitmap.set(pos)
        self.obj_map[node.obj].append(node)
        del node.obj
        for child in node.children:
            child.bitmap = BitMap(self.maximum_bits)
            child.bitmap |= node.bitmap
