# Cloud class for storage private information about credentials to 
class Cloud:
    def __init__(self,
                 id: int,
                 name: str,
                 cloud_type: str,
                 aws_region: str,
                 aws_key: str,
                 aws_secret_key: str,
                 azure_subscription_id: str,
                 azure_tenant_id: str,
                 azure_client_id: str,
                 azure_client_secret: str,
                 sync_state:int = 0,
                 sync_start:str = '',
                 sync_stop:str  = ''):
        self.id = id
        self.name = name
        self.cloud_type = cloud_type.upper()
        self.aws_region = aws_region
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.azure_subscription_id = azure_subscription_id
        self.azure_tenant_id = azure_tenant_id
        self.azure_client_id = azure_client_id
        self.azure_client_secret = azure_client_secret
        self.sync_state = sync_state
        self.sync_start = sync_start
        self.sync_stop  = sync_stop

        
    def to_dict(self) -> dict:
        return { 
              'id': self.id, 
              'name': self.name, 
              'cloud_type': self.cloud_type,
              'aws_region': self.aws_region,
              'aws_key': self.aws_key,               
              'azure_tenant_id': self.azure_tenant_id,
              'azure_client_id': self.azure_client_id,
              'azure_subscription_id': self.azure_subscription_id,
              'sync_state': self.sync_state,
              'sync_start': self.sync_start,
              'sync_stop': self.sync_stop,
            }

