from db import DB

class InternetNodes:
    def __init__(self):
        self.db   = DB()
        self.inodes = []

    def get(self):
        for n in self.db.get_internet_nodes():
            self.inodes.append(n[0])


    def to_dict(self):
        return [obj for obj in self.inodes]


def internet_nodes_encoder(obj):
    if isinstance(obj, InternetNodes):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

