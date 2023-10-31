// Clouds

export enum SyncState {
    Synced = 0,
    InSync = 1
}

export interface ICloud {
    id: number,
    name: string,
    cloud_type: 'AWS' | 'AZURE',
    aws_region: string,
    aws_key: string,
    aws_secret_key: string,
    azure_subscription_id: string,
    azure_tenant_id: string,
    azure_client_id: string,
    azure_client_secret: string,
    last_successful_sync?: string, 
    sync_state: SyncState, 
    sync_start?: string, 
    sync_stop?: string, 
    sync_msg?: string
}

export interface ICloudCreate extends Omit<ICloud, 'id' | 'sync_state' | 'sync_start' | 'sync_stop' | 'sync_msg' | 'last_successful_sync'> {

}

export interface ICloudView extends Omit<ICloud, 'aws_secret_key' | 'azure_client_secret'> {

}

