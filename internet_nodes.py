from db import DB

class InternetNodes:
    def __init__(self):
        self.db   = DB()
        self.inodes = []

    def get(self):
        for n in self.db.get_internet_nodes():
            self.inodes.append(n[0])

    def hide_pubip(self, ip_str: str):
        if ip_str == '0.0.0.0/0':
            return ip_str
        if ip_str == None or ip_str.find(".") == -1:
            return None
        l = ip_str.rsplit('.', 2)
        return f"XXX.XXX.{l[1]}.{l[2]}"

    def to_dict(self):
        return [self.hide_pubip(obj) for obj in self.inodes]


def internet_nodes_encoder(obj):
    if isinstance(obj, InternetNodes):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

