import { INode, ISubnet, IVM, IVPC } from "../core/models/IMap";

export type MapSelection = {
    type: 'vpc' | 'subnet' | 'vm' | 'network';
    key: string;
}