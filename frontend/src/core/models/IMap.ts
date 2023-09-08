export interface IVM {
    id: number;
    name: string;
    privateIP: string;
    publicIP: string;
}

export interface ISubnet {
    id: number;
    name: string;
    cidr: string;
    vms: IVM[];
}

export interface IVPC {
    id: number;
    name: string;
    cidr: string;
    subnets: ISubnet[];
}

export type INode = string;

export interface IMap {
    vpcs: IVPC[];
    inodes: INode[];
}
