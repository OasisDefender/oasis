import { useEffect, useState } from "react";
import { api } from "../api";
import { AxiosError } from "axios";
import { OasisDecodeError } from "../oasiserror";
import { IAnalyzation } from "../models/IAnalyzation";

export function useAnalyzation() {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [data, setData] = useState<IAnalyzation | null>(null);

    async function fetchData() {
        setLoading(true);
        setError(null);

        try {
            const response = await api.get<IAnalyzation>("/api/analyzation");
            setData(response.data);        
            setLoading(false);
        } catch (e: unknown) {
            setError(OasisDecodeError(e as AxiosError));            
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchData();
    }, []);


    return { loading, error, data };
}
