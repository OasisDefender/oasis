from .ctx import CTX  # base class for frontend objects
import sys

from .rule import Rule
from .db import DB
from .fw_aws import FW_AWS
from .fw_azure import FW_Azure


class VM_Rules(CTX):
    def __init__(self, vm_id: int, _db:DB = None):
        if _db != None:
            CTX.db = _db
        self.id: int = vm_id
        self.rules: list[Rule] = []  # links to

    def get(self):
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())
        rows = db.get_vm_rules(self.id)
        for row in rows:
            rule = Rule(id=row[0], group_id=row[1], rule_id=row[2].split('/')[-1], egress=row[3], proto=row[4],
                        port_from=row[5], port_to=row[6], naddr=row[7], cloud_id=row[8], ports=row[9])
            self.rules.append(rule)

    def to_dict(self):
        return [obj.to_gui_dict() for obj in self.rules]

    def delete_rules(self, rules: list[int]):
        cloud = None
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())

        cloud_info = db.get_cloud_vm_info(self.id)[0]
        cloud_type = cloud_info[0]
        cloud_id = cloud_info[2]
        group_id: list[str] = []

        if cloud_type == 'AWS':
            cloud = FW_AWS(_db=db)
        if cloud_type == 'AZURE':
            cloud = FW_Azure(_db=db)

        if cloud != None:
            # Delete rules from DB
            for rule in self.rules:
                db.delete_group_rules(cloud_id, rule.group_id)
                group_id.append(rule.group_id)

            # Delete rules from cloud
            cloud.connect(cloud_id)
            for del_rule in rules:
                for exist_rule in self.rules:
                    if del_rule == exist_rule.id:
                        # print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Rule found: {exist_rule.to_dict()}")
                        cloud.del_rule(exist_rule)
                        break

            # Sync rules from cloud
            g_ids = list(set(group_id))
            for g_id in g_ids:
                cloud.get_group_rules(cloud_id, g_id)

        else:
            print(
                f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Unsuported cloud type: {cloud_type}")

        return
