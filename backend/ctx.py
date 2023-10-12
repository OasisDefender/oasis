class CTX:
    user_id = None
    def __init__(self):
        pass
    def save_ctx(self, user_id:str = None):
        CTX.user_id = user_id
    def get_ctx(self) -> str:
        return CTX.user_id
