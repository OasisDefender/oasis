import { useEffect, useState } from "react";
import { ICloudCreate, ICloudView } from "../models/ICloud";
import { api } from "../api";
import { AxiosError } from "axios";
import { OasisDecodeError } from "../oasiserror";

export function useClouds() {
    const [loading, setLoading] = useState<boolean>(true);    
    const [error, setError] = useState<null | string>(null);
    const [clouds, setClouds] = useState<ICloudView[]>([]);
    
    async function fetchClouds() {
        setLoading(true);
        setError(null);

        try {
            const response = await api.get<ICloudView[]>("/api/clouds");
            setClouds(response.data);
            setLoading(false);
        } catch (e: unknown) {            
            setError(OasisDecodeError(e as AxiosError));
            setLoading(false);
        }
    }

    async function syncCloud(id: number) {
        await api.post(`/api/cloud/${id}/sync`);
    };

    async function deleteCloud(id: number) {
        await api.delete(`/api/cloud/${id}`);
        setClouds(clouds.filter((cloud) => cloud.id !== id));
    }

    async function addCloud(cloud: ICloudCreate) {
        const response = await api.post<ICloudView>('/api/cloud', JSON.stringify(cloud), {
            headers: {
                'Content-Type': 'application/json'
                }
        });
        setClouds([ response.data, ...clouds ]);
    }

    useEffect(() => {
        fetchClouds();
    }, []);

    return { loading, error, clouds, fetchClouds, syncCloud, deleteCloud, addCloud };
}
