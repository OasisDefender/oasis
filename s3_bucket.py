class S3_Bucket:
    def __init__(self, id: int, name: str, cloud_id: int):
        self.id       : str = id
        self.name     : str = name
        self.cloud_id : int = cloud_id


    def to_sql_values(self) -> dict:
        return {
            'id'       : self.id,
            'name'     : self.name,
            'cloud_id' : self.cloud_id
        }
