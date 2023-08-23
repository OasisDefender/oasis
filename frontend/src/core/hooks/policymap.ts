import { useState } from "react";
import { ChildrenInfo } from "../../components/UniversalMap/UniversalMapData";
import { api } from "../api";
import { OasisDecodeError } from "../oasiserror";
import { AxiosError } from "axios";

export function usePolicyMap() {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [data, setData] = useState<ChildrenInfo | undefined>(undefined);

    async function fetchData(classificationIds: number[]) {
        setLoading(true);
        setError(null);

        try {
            const response = await api.post<ChildrenInfo>('/api/classification', JSON.stringify(classificationIds), {
                headers: {
                    'Content-Type': 'application/json'
                    }
            });
            setData(response.data);        
            setLoading(false);
        } catch (e: unknown) {
            setError(OasisDecodeError(e as AxiosError));
            setLoading(false);
        }
    }


    return { loading, error, data, fetchData };
}
