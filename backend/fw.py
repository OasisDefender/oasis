import sys

from .ctx             import CTX  # base class for frontend objects
from .rule            import Rule
from .fw_aws          import FW_AWS
from .fw_azure        import FW_Azure
from .db              import DB
from network_service import NetworkService

class FW_Selected(CTX):
    def __init__(self, jsn: dict):
        # from JSON
        self.type        = "" # "vm"
        self.id          = "" # VM ID
        self.rules: Rule = [] # Rules list array
        # from DB
        self.cloud_type       = ""
        self.group_id         = ""
        self.cloud_id : int   = ""

    def get(self):
        db = DB(self.get_ctx())
        try:
            self.id   = jsn['selected']['id']
            self.type = jsn['selected']['type']

            rows = db.get_cloud_vm_info(self.id)
            for row in rows:
                #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: {row}")
                self.cloud_type = row[0]
                self.group_id   = row[1]
                self.cloud_id   = row[2]
                break

            #print(f"service: {jsn['rule']['service']}")
            if jsn['rule']['service'] == 'custom':
                try:
                    ports     = jsn['rule']['port'].split(",")
                except KeyError:
                    ports = f"{jsn['rule']['icmp_type']}-jsn['rule']['icmp_code']"

                if jsn['rule']['proto'].upper() == 'ICMP':
                    rule       = Rule(id=None,
                                    group_id=self.group_id,
                                    rule_id=None,
                                    egress=jsn['type'],
                                    proto=jsn['rule']['proto'],
                                    port_from=jsn['rule']['icmp_type'],
                                    port_to=jsn['rule']['icmp_code'],
                                    naddr=jsn['rule']['ip'],
                                    cloud_id=self.cloud_id,
                                    ports=None
                                )
                    self.rules.append(rule)
                    #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: {rule.to_sql_values()}")

                if jsn['rule']['proto'].upper() == 'TCP' or jsn['rule']['proto'].upper() == 'UDP':
                    for port in ports:
                        p = port.split('-')
                        try:
                            port2 = p[1].strip()
                        except IndexError:
                            port2 = '' # TODO: Check in DB for current value in empty last port
                        rule = Rule(id=None,
                                    group_id=self.group_id,
                                    rule_id=None,
                                    egress=jsn['type'],
                                    proto=jsn['rule']['proto'],
                                    port_from=p[0].strip(),
                                    port_to=port2,
                                    naddr=jsn['rule']['ip'],
                                    cloud_id=self.cloud_id,
                                    ports=port
                                )
                        self.rules.append(rule)
                        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: {rule.to_sql_values()}")
            else:
                for s in db.get_services_by_name(jsn['rule']['service']):
                    print(f"service: {s.to_dict()}")
                    rule = Rule(id=None,
                                group_id=self.group_id,
                                rule_id=None,
                                egress=jsn['type'],
                                proto=s.proto.upper(),
                                port_from=s.port,
                                port_to=s.port,
                                naddr=jsn['rule']['ip'],
                                cloud_id=self.cloud_id,
                                ports=s.port
                            )
                    self.rules.append(rule)



        except KeyError:
            pass
        pass


    def __add_rules_aws(self):
        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Not implemented!")
        aws = FW_AWS()
        aws.connect(self.cloud_id)
        for rule in self.rules:
            status: bool = aws.add_rule(rule, self.group_id)
            if not status:
                break

    def __add_rules_azure(self):
        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Not implemented!")
        cloud = FW_Azure()
        cloud.connect(self.cloud_id)
        for rule in self.rules:
            status: bool = cloud.add_rule(rule, self.group_id)
            if not status:
                break

    def add_rules(self):
        #print(self.cloud_type)
        if self.cloud_type == 'AWS':
            self.__add_rules_aws()
        if self.cloud_type == 'AZURE':
            self.__add_rules_azure()


    def sync_rules(self):
        cloud = None
        db = DB(self.get_ctx())

        if self.cloud_type == 'AWS':
            cloud = FW_AWS()
        if self.cloud_type == 'AZURE':
            cloud = FW_Azure()

        if cloud != None:
            cloud.save_ctx(self.get_ctx())
            db.delete_group_rules(self.cloud_id, self.group_id)
            cloud.connect(self.cloud_id)
            cloud.get_group_rules(self.cloud_id, self.group_id)



    def to_dict(self):
        return {
            'self.cloud_type' : self.cloud_type,
            'self.group_id'   : self.group_id,
            'type'            : self.type,
            'id'              : self.id,
            'rules'           : [obj.to_dict() for obj in self.rules]
        }


def FW_Selected_encoder(obj):
    if isinstance(obj, FW_Selected):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
