from .ctx import CTX  # base class for frontend objects
from .db import DB
from .rule import Rule


class RuleGroup(CTX):
    def __init__(self, rg_row: list[str] = None, id: int = 0, if_id: str = '', subnet_id: str = '', name: str = '', type: str = '', cloud_id: int = 0, _db:DB = None):
        if _db != None:
            CTX.db = _db

        if rg_row != None:  # load from DB
            self.id: int = rg_row[0]
            self.if_id: str = rg_row[1]
            self.subnet_id: str = rg_row[2]
            self.name: str = rg_row[3]
            self.type: str = rg_row[4]
            self.cloud_id: int = rg_row[5]
        else:  # load from cloud
            self.id: str = id
            self.if_id: str = if_id
            self.subnet_id: str = subnet_id
            self.name: str = name
            self.type: str = type
            self.cloud_id: int = cloud_id

    def to_sql_values(self) -> dict:
        return {
            'id': self.id,
            'if_id': self.if_id,
            'name': self.name,
            'type': self.type,
            'cloud_id': self.cloud_id,
            'subnet_id': self.subnet_id
        }


def get_all_rule_groups(user_id:str = None, _db:DB = None) -> list[RuleGroup]:
    db:DB = None
    if _db != None:
        db = _db
    else:
        db = DB(user_id)
    rgs: list[RuleGroup] = []
    for row in db.get_all_rule_groups():
        rg = RuleGroup(rg_row=row, _db=db)
        rg.save_ctx(user_id)
        # print(f"rg: {rg.to_sql_values()}")
        rgs.append(rg)
    return rgs


class RuleGroupNG(CTX):
    def __init__(self, sg_id: int, if_ids: list[str], subnet_ids: list[str], name: str, type: str, cloud_id: int, rules: list[Rule]):
        # self.id = sg_id
        self.if_ids = if_ids
        self.subnet_ids = subnet_ids
        self.name = name
        self.type = type
        self.cloud_id = cloud_id
        self.rules = rules

    def add_rule(self, r: Rule):
        # for t in self.rules:
        #    if t.rule_id == r.rule_id:
        #        return
        self.rules.append(r)

    def add_if(self, if_id: str):
        self.if_ids.append(if_id)

    def add_subnet(self, subnet_id: str):
        self.subnet_ids.append(subnet_id)


def convert_RuleGroup_to_NG(sgs: list[RuleGroup], rules: list[Rule]):
    sgs_NG = {}
    for sg in sgs:
        key = (sg.cloud_id, sg.name)
        if sgs_NG.get(key, None) == None:
            sg_NG = RuleGroupNG(sg.id, [], [], sg.name,
                                sg.type, sg.cloud_id, [])
            for r in rules:
                if r.cloud_id == sg.cloud_id and r.group_id == sg.name:
                    sg_NG.add_rule(r)
            sgs_NG[key] = sg_NG

        if sg.subnet_id == None or sg.subnet_id == "":
            if sg.if_id == '' or sg.if_id == None:
                continue
            sgs_NG[key].add_if(sg.if_id)
        else:
            sgs_NG[key].add_subnet(sg.subnet_id)

    return list(sgs_NG.values())
