from db import DB

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

    def to_typescript_values(self) -> dict:
        return {
            'id'    : f"{self.id}",
            'type'  : "Bucket",
            'label' : self.name,
            'info'  : [
                {
                    'icon': "IconWorld",
                    'tooltip': self.name,
                },
            ],
        }
        


class S3_Cloud:
    def __init__(self, id: int, name: str, type: str):
        self.id      : str = id
        self.name    : str = name
        self.type    : int = type
        self.buckets : list[S3_Bucket] = []

    def get_buckets(self):
        db = DB()
        for bucket_info in db.get_s3_buckets(cloud_id=self.id):
            b = S3_Bucket(id=bucket_info[0], name=bucket_info[1], cloud_id=bucket_info[2])
            self.buckets.append(b)


    def to_typescript_values(self) -> dict:
        return {
            'id'    : f"{self.id}",
            'type'  : "Cloud",
            'label' : self.name,
            'info'  : [
                {
                    'icon': "IconWorld",
                    'tooltip': self.type,
                },
            ],
            'childrenLayout': "column",
            'children': [obj.to_typescript_values() for obj in self.buckets]
        }
