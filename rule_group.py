class RuleGroup:
    def __init__(self, id: int, if_id: str, name: str, type: str, cloud_id: int ):
        self.id       : str = id
        self.if_id    : str = if_id
        self.name     : str = name
        self.type     : str = type
        self.cloud_id : int = cloud_id


    def to_sql_values(self) -> dict:
        return {
            'id'       : self.id,
            'if_id'    : self.if_id,
            'name'     : self.name,
            'type'     : self.type,
            'cloud_id' : self.cloud_id
        }
