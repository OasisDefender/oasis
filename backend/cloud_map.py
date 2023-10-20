from .ctx import CTX # base class for frontend objects
from .vpc import VPC
from .db  import DB

class CloudMap(CTX):
    def __init__(self, _db:DB = None):
        self.vpcs: list[VPC] = []
        if _db != None:
            CTX.db = _db

    def get(self):
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())

        for vpc_info in db.get_vpcs_info():
            v = VPC(vpc=vpc_info, _db = db)
            v.save_ctx(self.get_ctx())
            v.get_subnet_info()
            self.vpcs.append(v)

    def to_dict(self):
        return [obj.to_dict() for obj in self.vpcs]


def cloud_map_encoder(obj):
    if isinstance(obj, CloudMap):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

