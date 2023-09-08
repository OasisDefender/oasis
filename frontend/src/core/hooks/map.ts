import { useEffect, useState } from "react";
import { IMap } from "../models/IMap";
import { api } from "../api";
import { AxiosError } from "axios";
import { OasisDecodeError } from "../oasiserror";
import { ILinks } from "../models/ILinks";

export function useMap() {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [themap, setTheMap] = useState<IMap | null>(null);

    async function addTarget({target} : {target : string}) {
        if (themap) {
            setTheMap({...themap, inodes: [...themap.inodes, target] });
        }
    }

    async function fetchMap() {
        setLoading(true);
        setError(null);

        try {
            const response = await api.get<IMap>("/api/map");
            setTheMap(response.data);
            setLoading(false);
        } catch (e: unknown) {
            setError(OasisDecodeError(e as AxiosError));
            setLoading(false);
        }
    }

    async function getLinksVM(vmId: number) {
        const response = await api.get<ILinks>(`/api/vm/${vmId}/links`);
        return response.data;
    }

    useEffect(() => {
        fetchMap();
    }, []);


    return { loading, error, themap, addTarget, getLinksVM };
}
