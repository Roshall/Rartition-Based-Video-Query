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
        obj = node.obj
        pos = obj_pos_map[obj.id]
        node.bitmap.set(pos)
        # add the node to the hash index
        fi_node = FasterIndex.Node(node.bitmap, node.obj.my_frames)
        obj_map[obj.id].append(fi_node)
        # set the bitmaps for all his children
        # not sure if here is the best place to set them
        for child in node.children:
            child.bitmap = BitMap(maximum_bits)
            child.bitmap |= node.bitmap
        del node.bitmap

    return visit_node


class FasterIndex:
    """
    hash index plus bitmaps
    """
    class Node:
        def __init__(self, bitmap, my_frames: list):
            self.bitmap = bitmap
            self.my_frames = my_frames
            self.score = len(my_frames)

    def __init__(self, obj_ids: list, obj_pos_map, sopt_forest):
        self.obj_map = {}
        self.sorted_nodes = None
        for obj in obj_ids:
            self.obj_map[obj] = []
        maximum_bits = len(obj_ids)
        self.__build(sopt_forest, obj_pos_map, maximum_bits)

    def __build(self, sopt_forest: list, obj_pos_map, maximum_bits):
        """ building hash and bitmap index for each tree in the SOPT forest
        """
        for tree in sopt_forest:
            tree.bitmap = BitMap(maximum_bits)
            bfs(tree, visit_node4faster_index(self.obj_map, obj_pos_map, maximum_bits))
        self.__sort_node()

    def __sort_node(self):
        """
        node are sorted according to the bitmap cardinality in descending order,
        breaking ties using the score. Therefore, the node with maximal score
        will be the last one.
        :return: sorted node list
        """
        nodes = []
        for _, v in self.obj_map.items():
            nodes.extend(v)

        nodes.sort(key=lambda n: (-n.bitmap.count(), n.score))
        self.sorted_nodes = nodes

    def get(self, obj_id):
        if (exam := self.obj_map.get(obj_id)) is None:
            return None
        else:
            return iter(exam)
