from db import DB

class Destination:
    def __init__(self, row, type):
        row_4: str = row[4]
        
        self.type     = type
        self.id       = row[0]
        self.inbound  = []
        self.outbound = []
        self.address  = row[3]

        if row_4 == '*':
            row_4 = 'Any'
        if row_4 == '0':
            row_4 = 'Any'

        db        = DB()
        srvc: str = db.detect_service(row[2], row[4], '')
        if srvc == '':
            srvc = f"{row[2]}/{row_4}"

        if row[1] == "False": #inbound
            self.inbound.append(srvc)
        else:              #outbound
            self.outbound.append(srvc)


    def is_empty(self):
        status = 0
        if self.inbound == "" and self.outbound == "":
            status = 1
        return status
        

    def to_dict(self):
        inbound   = list(set(self.inbound))
        outbound  = list(set(self.outbound))
        if self.type == "network":
            return {
                "to": { "type": self.type, "address": self.address},
                "inbound":  ', '.join(inbound),
                "outbound": ', '.join(outbound)
            }
        else:
            return {
                "to": { "type": self.type, "id": self.id},
                "inbound":  ', '.join(inbound),
                "outbound": ', '.join(outbound)
            }


def destination_encoder(obj):
    if isinstance(obj, Destination):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
