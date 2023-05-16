from vpc import VPC
from db  import DB

class CloudMap:
    def __init__(self):
        self.db   = DB()
        self.vpcs: list[VPC] = []


    def get(self):
        for vpc_info in self.db.get_vpcs_info():
            v = VPC(vpc=vpc_info)
            self.vpcs.append(v)


    def to_dict(self):
        return [obj.to_dict() for obj in self.vpcs]


def cloud_map_encoder(obj):
    if isinstance(obj, CloudMap):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

