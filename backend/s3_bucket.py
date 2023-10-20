from .ctx import CTX  # base class for frontend objects
from .db import DB

class S3_Bucket(CTX):
    def __init__(self, id: int, name: str, cloud_id: int, _db:DB = None):
        if _db != None:
            CTX.db = _db
        self.id       : str = id
        self.name     : str = name
        self.cloud_id : int = cloud_id


    def to_sql_values(self) -> dict:
        return {
            'id'       : self.id,
            'name'     : self.name,
            'cloud_id' : self.cloud_id
        }

    def to_typescript_values(self) -> dict:
        return {
            'id'    : f"{self.id}",
            'type'  : "Bucket",
            'label' : self.name,
            'info'  : [
                {
                    'icon': "IconInfoCircle",
                    'tooltip': self.name,
                },
            ],
        }


class S3_Cloud(CTX):
    def __init__(self, id: int, name: str, type: str, _db:DB = None):
        if _db != None:
            CTX.db = _db
        self.id      : str = id
        self.name    : str = name
        self.type    : int = type
        self.buckets : list[S3_Bucket] = []

    def get_buckets(self):
        db:DB = None
        if CTX.db != None:
            db = CTX.db
        else:
            db = DB(self.get_ctx())
        for bucket_info in db.get_s3_buckets(cloud_id=self.id):
            b = S3_Bucket(id=bucket_info[0], name=bucket_info[1], cloud_id=bucket_info[2])
            b.save_ctx(self.get_ctx())
            self.buckets.append(b)


    def to_typescript_values(self) -> dict:
        return {
            'id'    : f"{self.id}",
            'type'  : "Cloud",
            'label' : self.name,
            'info'  : [
                {
                    'icon': "IconInfoCircle",
                    'tooltip': self.type,
                },
            ],
            'childrenLayout': "column",
            'children': [obj.to_typescript_values() for obj in self.buckets]
        }
