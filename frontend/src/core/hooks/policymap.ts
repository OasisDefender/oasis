import { useCallback, useState } from "react";
import {
    ChildItem,
    ChildrenInfo,
    DEFAULT_COLLAPSED,
    UniversalMapInfo,
} from "../../components/UniversalMap/UniversalMapData";
import { api } from "../api";
import { OasisDecodeError } from "../oasiserror";
import { AxiosError } from "axios";

const toggleItemById = (id: string, items: ChildItem[]): ChildItem[] => {
    let changed = false;

    const updatedItems = items.map((item) => {
        if (item.id === id) {
            changed = true;
            return {
                ...item,
                childrenCollapsed: !(
                    item.childrenCollapsed ?? DEFAULT_COLLAPSED
                ),
            };
        }

        if (item.children) {
            const updatedChildren = toggleItemById(id, item.children);
            if (updatedChildren !== item.children) {
                changed = true;
                return {
                    ...item,
                    children: updatedChildren,
                };
            }
        }

        return item;
    });

    return changed ? updatedItems : items;
};

export function usePolicyMap() {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [data, setData] = useState<UniversalMapInfo | undefined>(undefined);

    async function fetchData(classificationIds: number[]) {
        setLoading(true);
        setError(null);

        try {
            const response = await api.post<UniversalMapInfo>(
                "/api/classification2",
                JSON.stringify(classificationIds),
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            );
            setData(response.data);
            setLoading(false);
        } catch (e: unknown) {
            setError(OasisDecodeError(e as AxiosError));
            setLoading(false);
        }
    }

    const toogleChildren = useCallback((id: string) => {
        setData((oldData) => {
            if (!oldData) return oldData;
            const newData: ChildrenInfo = {
                children: toggleItemById(id, oldData.scheme.children ?? []),
                childrenLayout: oldData.scheme.childrenLayout,
            };
            return {
                lines: oldData.lines,
                scheme: newData,
            };
        });
    }, []);

    return { loading, error, data, fetchData, toogleChildren };
}
