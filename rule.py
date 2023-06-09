import sys

from db import DB

class Rule:
    def __init__(self, id: int, group_id: str, rule_id: str, egress: str, proto: str,
                 port_from: str, port_to: str, naddr: str, cloud_id: int, ports: str):
        self.id        : int = id
        self.group_id  : str = group_id
        self.rule_id   : str = rule_id
        self.egress    : str = egress
        self.proto     : str = proto
        self.port_from : str = port_from
        self.port_to   : str = port_to
        self.naddr     : str = None
        self.cloud_id  : int = cloud_id
        self.ports     : str = ports

        ip = naddr.split('/')
        if len(ip) == 1:
            self.naddr = f"{naddr}/32"
        else:
            self.naddr = naddr


    def to_dict(self):
        rule_type = 'inbound' if self.egress == 'False' else 'outbound'
        ''' AWS not support IP rules!
        if self.proto.upper() == 'IP':
            return {
                'type'  : rule_type,
                'ip'    : self.naddr,
                'proto' : self.proto
            }
        '''
        if self.proto.upper() == 'TCP' or self.proto.upper() == 'UDP':
            return {
                'type'  : rule_type,
                'ip'    : self.naddr,
                'proto' : self.proto,
                'port'  : self.port_from if self.port_to == '' else f"{self.port_from}-{self.port_to}"
            }
        if self.proto.upper() == 'ICMP':
            return {
                'type'  : rule_type,
                'ip'    : self.naddr,
                'proto' : self.proto,
                'icmp_type'  : self.port_from,
                'icmp_code'  : self.port_to
            }


    def to_sql_values(self) -> dict:
        return {
            'id'        : self.id,
            'group_id'  : self.group_id,
            'rule_id'   : self.rule_id,
            'egress'    : self.egress,
            'proto'     : self.proto,
            'port_from' : self.port_from,
            'port_to'   : self.port_to,
            'naddr'     : self.naddr,
            'cloud_id'  : self.cloud_id,
            'ports'     : self.ports
        }


    def to_gui_dict(self) -> dict:
        ports: str = self.ports
        if ports[0] == '0':
            ports = 'Any'
        if ports[0] == '*':
            ports = 'Any'
        db        = DB()
        srvc: str = db.detect_service(self.proto, self.port_from, self.port_to)
        if srvc == '':
            return {
                'id'        : self.id,
                'group_id'  : self.group_id.split('/')[-1],
                #'rule_id'   : self.rule_id,
                'egress'    : 'Inbound' if self.egress == 'False' else 'Outbound',
                'proto'     : self.proto,
                #'port_from' : self.port_from,
                #'port_to'   : self.port_to,
                'naddr'     : self.naddr,
                'cloud_id'  : self.cloud_id,
                'ports'     : ports
            }
        else:
            #print(f"to_gui_dict(): test: '{srvc}'")
            return {
                'id'        : self.id,
                'group_id'  : self.group_id.split('/')[-1],
                #'rule_id'   : self.rule_id,
                'egress'    : 'Inbound' if self.egress == 'False' else 'Outbound',
                'proto'     : srvc,
                #'port_from' : self.port_from,
                #'port_to'   : self.port_to,
                'naddr'     : self.naddr,
                'cloud_id'  : self.cloud_id,
                'ports'     : ports
            }


