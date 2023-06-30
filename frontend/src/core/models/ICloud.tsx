// Clouds

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
    azure_client_secret: string
}

export interface ICloudCreate extends Omit<ICloud, 'id'> {

}

export interface ICloudView extends Omit<ICloud, 'aws_secret_key' | 'azure_client_secret'> {

}

