"""
Public testing utility functions.
"""


class DebugDir:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def __enter__(self):
        self.dir_path.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, ty, val, tb):
        pass
