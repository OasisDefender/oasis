import { useEffect, useState } from "react";
import { api } from "../api";
import { AxiosError } from "axios";
import { OasisDecodeError } from "../oasiserror";
import { IInitSettings } from "../models/IInitSettings";

export function useInitSettings() {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [data, setData] = useState<IInitSettings | null>(null);

    async function fetchData() {
        setLoading(true);
        setError(null);

        try {
            const response = await api.get<IInitSettings>("/api/init");
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
