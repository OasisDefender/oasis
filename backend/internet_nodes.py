from .ctx import CTX # base class for frontend objects
from .db import DB

class InternetNodes(CTX):
    def __init__(self, _db:DB = None):
        if _db != None:
            CTX.db = _db
        self.inodes = []

    def get(self):
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())
        for n in db.get_internet_nodes():
            self.inodes.append(n[0])

    def to_dict(self):
        return [obj for obj in self.inodes]


def internet_nodes_encoder(obj):
    if isinstance(obj, InternetNodes):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
