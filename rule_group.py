from db import DB

class RuleGroup:
    def __init__(self, rg_row: list[str], id:int = 0, if_id:str = '', subnet_id:str = '', name:str = '', type:str = '', cloud_id:int = 0):
        if rg_row != None: # load from DB
            self.id       : int = rg_row[0]
            self.if_id    : str = rg_row[1]
            self.subnet_id: str = rg_row[2]
            self.name     : str = rg_row[3]
            self.type     : str = rg_row[4]
            self.cloud_id : int = rg_row[5]
        else: # load from cloud
            self.id       : str = id
            self.if_id    : str = if_id
            self.subnet_id: str = subnet_id
            self.name     : str = name
            self.type     : str = type
            self.cloud_id : int = cloud_id


    def to_sql_values(self) -> dict:
        return {
            'id'       : self.id,
            'if_id'    : self.if_id,
            'name'     : self.name,
            'type'     : self.type,
            'cloud_id' : self.cloud_id,
            'subnet_id': self.subnet_id
        }

def get_all_rule_groups() -> list[RuleGroup]:
    db                   = DB()
    rgs: list[RuleGroup] = []
    for row in db.get_all_rule_groups():
        rg = RuleGroup(row)
        #print(f"rg: {rg.to_sql_values()}")
        rgs.append(rg)
    return rgs
