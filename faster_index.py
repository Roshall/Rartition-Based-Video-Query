from bitmap import BitMap
from utils import breath_first_search as bfs


def visit_node4faster_index(obj_pos_map, obj_map, maximum_bits):
    """
    visit sopt and build faster index
    :param obj_pos_map: the pos of the object in bitmap
    :param obj_map: the hash index, this function will add to the index all objects in the sopt tree
    :param maximum_bits: the number of object
    :return: a function that can be passed to bfs function.

    also notice that the root's bitmap shall be initialized manually before
    call this function
    """

    def visit_node(node):
        # set the node's object's corresponding pos to 1 in the bitmap
        pos = obj_pos_map[node.obj]
        node.bitmap.set(pos)
        # add the node to the hash index
        obj_map[node.obj].append(node)
        del node.obj  # no longer needed
        # set the bitmaps for all his children
        # not sure if here is the best place to set them
        for child in node.children:
            child.bitmap = BitMap(maximum_bits)
            child.bitmap |= node.bitmap

    return visit_node


class FasterIndex:
    def __init__(self, objs: list):
        self.maximum_bits = len(objs)
        self.objs = objs
        self.obj_map = {}
        self.obj_pos_map = {}
        self.sorted_nodes = None

        for i, obj in enumerate(objs):
            self.obj_pos_map[obj] = i
            self.obj_map[obj] = []

    def build(self, sopt_forest: list):
        """ building hash and bitmap index for each tree in SOPT forest
        """
        for tree in sopt_forest:
            tree.bitmap = BitMap(self.maximum_bits)
            bfs(tree, visit_node4faster_index(self.obj_pos_map, self.obj_map, self.maximum_bits))
        self.__sort_node()

    def __sort_node(self):
        nodes = []
        for _, v in self.obj_map.items():
            nodes.extend(v)

        nodes.sort(key=lambda n: (len(n.bitmap.nonzero()), n.score))
        self.sorted_nodes = nodes

    def whole_seq_of(self, node):
        """
        get the whole sequence that a node represents
        :param node: sopt tree node
        :return: seq list
        """
        seq = []
        for pos in node.bitmap.nonzero():
            seq.append(self.objs[pos])
        return seq
