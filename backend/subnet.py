from ctx import CTX # base class for frontend objects
from db import DB
from vm import VM


class Subnet(CTX):
    def __init__(self, subnet: list[str], name: str = None, arn: str = None, network: str = None, azone: str = None,
                 note: str = None, vpc_id: str = None, cloud_id: int = None, _db:DB = None):
        if _db != None:
            CTX.db = _db
        if subnet != None:
            # load from DB
            self.id: int = subnet[0]
            self.name: str = subnet[1]
            self.arn: str = subnet[2]
            self.network: str = subnet[3]
            self.azone: str = subnet[4]
            self.note: str = subnet[5]
            self.vpc_id: str = subnet[6]
            self.cloud_id: int = subnet[7]
            self.vms: list[VM] = []
        else:
            # load from cloud
            self.id: int = None
            self.name: str = name
            self.arn: str = arn
            self.network: str = network
            self.azone: str = azone
            self.note: str = note
            self.vpc_id: str = vpc_id
            self.cloud_id: int = cloud_id
            self.vms: list[VM] = []

    def get_vms_info(self):
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())
        for vm in db.get_vms_info(self.name):
            m = VM(vm=vm)
            m.save_ctx(self.get_ctx())
            self.vms.append(m)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.note,
            'cidr': self.network,
            'vms': [obj.to_dict() for obj in self.vms]
        }

    def to_sql_values(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'arn': self.arn,
            'network': self.network,
            'azone': self.azone,
            'note': self.note,
            'vpc_id': self.vpc_id,
            'cloud_id': self.cloud_id
        }


def subnet_encoder(obj):
    if isinstance(obj, Subnet):
        return obj.to_dict()
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable")
