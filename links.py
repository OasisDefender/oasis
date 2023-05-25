from db          import DB
from destination import Destination


class Links:
    def __init__(self, id):
        self.db  = DB()                   # SQL db
        self.id  = id                     # VM ID
        self.dst : list[Destination] = [] # links to

    def get(self):
        row_4: str = None
        db        = DB()
        srvc: str = ''

        # Load link with type - network
        d : Destination = None
        for rule in self.db.get_link_networks(self.id):
            row_4 = rule[4]
            if row_4 == '*':
                row_4 = 'Any'
            if row_4 == '0':
                row_4 = 'Any'

            srvc = db.detect_service(rule[2], row_4, '')
            if srvc == '':
                srvc = f"{rule[2]}/{row_4}"
            
            if d is None:
                d = Destination(rule, "network")
            else:
                if d.address == rule[3]:
                    # Inbound                                
                    if rule[1] == "False":
                        d.inbound.append(srvc)
                    # Outbound
                    else:
                        d.outbound.append(srvc)
                else:
                    if d.is_empty() == 0:
                        self.dst.append(d)
                    d = Destination(rule, "network")
        if d != None:
            if d.is_empty() == 0:
                self.dst.append(d)

        # Load link with type - vpc
        d : Destination = None
        for rule in self.db.get_link_vpcs(self.id):
            row_4 = rule[4]
            if row_4 == '*':
                row_4 = 'Any'
            if row_4 == '0':
                row_4 = 'Any'

            srvc = db.detect_service(rule[2], row_4, '')
            if srvc == '':
                srvc = f"{rule[2]}/{row_4}"
            
            if d is None:
                d = Destination(rule, "vpc")
            else:
                if d.address == rule[3]:
                    #inbound
                    if rule[1] == "False":
                        d.inbound.append(srvc)
                    #outbound
                    else:
                        d.outbound.append(srvc)
                else:
                    if d.is_empty() == 0:
                        self.dst.append(d)
                    d = Destination(rule, "vpc")
        if d != None:
            if d.is_empty() == 0:
                self.dst.append(d)

        # Load link with type - subnet
        d : Destination = None
        for rule in self.db.get_link_subnets(self.id):
            row_4 = rule[4]
            if row_4 == '*':
                row_4 = 'Any'
            if row_4 == '0':
                row_4 = 'Any'

            srvc = db.detect_service(rule[2], row_4, '')
            if srvc == '':
                srvc = f"{rule[2]}/{row_4}"

            if d is None:
                d = Destination(rule, "subnet")
            else:
                if d.address == rule[3]:
                    #inbound
                    if rule[1] == "False":
                        d.inbound.append(srvc)
                    #outbound
                    else:
                        d.outbound.append(srvc)
                else:
                    if d.is_empty() == 0:
                        self.dst.append(d)
                    d = Destination(rule, "subnet")
        if d != None:
            if d.is_empty() == 0:
                self.dst.append(d)
        
        # Load link with type - vm
        d : Destination = None
        for rule in self.db.get_link_vms(self.id):
            row_4 = rule[4]
            if row_4 == '*':
                row_4 = 'Any'
            if row_4 == '0':
                row_4 = 'Any'

            srvc = db.detect_service(rule[2], row_4, '')
            if srvc == '':
                srvc = f"{rule[2]}/{row_4}"

            if d is None:
                d = Destination(rule, "vm")
            else:
                if d.address == rule[3]:
                    #inbound                    
                    if rule[1] == "False":
                        d.inbound.append(srvc)
                    #outbound
                    else:
                        d.outbound.append(srvc)
                else:
                    if d.is_empty() == 0:
                        self.dst.append(d)
                    d = Destination(rule, "vm")
        if d != None:
            if d.is_empty() == 0:
                self.dst.append(d)
        return

    def to_dict(self):
        return [obj.to_dict() for obj in self.dst]

def link_encoder(obj):
    if isinstance(obj, Links):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
