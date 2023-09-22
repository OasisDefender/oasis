import { useEffect, useState } from "react";
import { IHeaderInfo } from "../models/IHeaderInfo";
import { api } from "../api";

export function useHeaderInfo() {
    const [maxSeverity, setMaxSeverity] = useState<number | undefined>(undefined);

    async function fetch() {
        try {
            const response = await api.get<IHeaderInfo>("/api/header-info");
            setMaxSeverity(response.data.maxSeverity);
        } catch (e: unknown) {
            setMaxSeverity(undefined);
        }
    }

    useEffect(() => {
        fetch();
    }, []);


    return { fetch, maxSeverity };
}