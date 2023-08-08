class RuleGroup:
    def __init__(self, id = 0, if_id = '', subnet_id = '', name = '', type = '', cloud_id = 0):
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
