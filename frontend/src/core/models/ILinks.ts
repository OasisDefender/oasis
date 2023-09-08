export interface ITo {
    type: 'vpc' | 'subnet' | 'vm' | 'network';
    address?: string;
    id?: number;
}

export interface ILink {
    to: ITo;
    inbound: string;
    outbound: string;
}

export interface IRule {
    id: number;
    group_id: string;
    egress: string;
    proto: string;
    naddr: string;
    cloud_id: number;
    ports: string;
}

export interface ILinks {
    links: ILink[];
    rules: IRule[];
}
