from utils import add_id_for


class FrameReader:
    def frame_list(self):
        """ one frame shouldn't have identical object"""
        pass


class DummyFrameReader(FrameReader):
    def frame_list(self, has_id=True):
        f = [[2, 3],
             [1, 3],
             [1, 2, 3],
             [1, 4],
             [3],
             [3],
             [2, 4],
             [1, 2, 4]]

        if has_id:
            f = add_id_for(f, 0)
        return f
