class FrameReader:
    def frame_list(self):
        """ one frame shouldn't have identical object"""
        pass


class DummyFrameReader(FrameReader):
    def frame_list(self):
        f = [[2, 3],
             [1, 3],
             [1, 2, 3]]
        return f
