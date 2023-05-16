class VM:

    def __init__(self, vm: list[str], type: str=None, vpc_id: str=None, azone: str=None, subnet_id: str=None, name: str=None,
                 privdn: str=None, privip: str=None, pubdn: str=None, pubip: str=None, note: str=None, os: str=None,
                 state: str=None, mac: str=None, if_id: str=None, cloud_id: int=None):
        if vm != None:
            # load from DB
            self.id        : int = vm[0]
            self.type      : str = vm[1]
            self.vpc_id    : str = vm[2]
            self.azone     : str = vm[3]
            self.subnet_id : str = vm[4]
            self.name      : str = vm[5]
            self.privdn    : str = vm[6]
            self.privip    : str = vm[7]
            self.pubdn     : str = vm[8]
            self.pubip     : str = vm[9]
            self.note      : str = vm[10]
            self.os        : str = vm[11]
            self.state     : str = vm[12]
            self.mac       : str = vm[13]
            self.if_id     : str = vm[14]
            self.cloud_id  : int = vm[15]
        else:
            # load from cloud
            self.id        : int = None
            self.type      : str = type
            self.vpc_id    : str = vpc_id
            self.azone     : str = azone
            self.subnet_id : str = subnet_id
            self.name      : str = name
            self.privdn    : str = privdn
            self.privip    : str = privip
            self.pubdn     : str = pubdn
            self.pubip     : str = pubip
            self.note      : str = note
            self.os        : str = os
            self.state     : str = state
            self.mac       : str = mac
            self.if_id     : str = if_id
            self.cloud_id  : int = cloud_id


    def to_dict(self):
        return {
            'id'        : self.id,
            'name'      : self.note,
            'privateIP' : self.privip,
            'publicIP'  : self.pubip
        }


    def to_sql_values(self) -> dict:
        return {
            'id'        : self.id,
            'type'      : self.type,
            'vpc_id'    : self.vpc_id,
            'azone'     : self.azone,
            'subnet_id' : self.subnet_id,
            'name'      : self.name,
            'privdn'    : self.privdn,
            'privip'    : self.privip,
            'pubdn'     : self.pubdn,
            'pubip'     : self.pubip,
            'note'      : self.note,
            'os'        : self.os,
            'state'     : self.state,
            'mac'       : self.mac,
            'if_id'     : self.if_id,
            'cloud_id' : self.cloud_id
        }


def vm_encoder(obj):
    if isinstance(obj, VM):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
