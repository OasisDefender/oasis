from db import DB
import sys

class CTX:
    user_id = None
    db:DB   = None
    def __init__(self, _db:DB = None):
        if _db != None:
            CTX.db = _db
    def save_ctx(self, user_id:str = None):
        CTX.user_id = user_id
    def get_ctx(self) -> str:
        return CTX.user_id
