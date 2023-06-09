from db     import DB
from subnet import Subnet


class VPC:
    def __init__(self, vpc: list[str], name: str=None, network: str=None, cloud_id: int=None, note: str=None):
        self.db = DB()
        if vpc != None:
            # load from DB
            self.id:       int          = vpc[0]
            self.name:     str          = vpc[3]
            self.network:  str          = vpc[2]
            self.cloud_id: int          = vpc[4]
            self.note:     str          = vpc[5]
            self.subnets:  list[Subnet] = []
            for subnet_info in self.db.get_subnets_info(vpc[1]):
                s = Subnet(subnet=subnet_info)
                self.subnets.append(s)
        else:
            # load from cloud
            self.id:       int          = None
            self.name:     str          = name
            self.network:  str          = network
            self.cloud_id: int          = cloud_id
            self.note:     str          = note
            self.subnets:  list[Subnet] = []


    def to_dict(self) -> dict:
        return {
            'id'      : self.id,
            'name'    : self.name,
            'cidr'    : self.network,
            'subnets' : [obj.to_dict() for obj in self.subnets]
        }


    def to_sql_values(self) -> dict:
        return {
            'id'       : self.id,
            'name'     : self.name,
            'network'  : self.network,
            'cloud_id' : self.cloud_id,
            'note'     : self.note,
        }


def vpc_encoder(obj):
    if isinstance(obj, VPC):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
