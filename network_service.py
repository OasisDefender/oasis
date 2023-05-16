class NetworkService:
    def __init__(self, id: int, name: str, proto: str, port: str):
        self.id    : int = id
        self.name  : str = name
        self.proto : str = proto
        self.port  : str = port


    def to_dict(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
            'proto' : self.proto,
            'port'  : self.port
        }
