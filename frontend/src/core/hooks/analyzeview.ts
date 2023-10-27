import { useCallback, useRef, useState } from "react";
import {
    ChildItem,
    ChildrenInfo,
    DEFAULT_COLLAPSED,
    LineInfo,
    LineItem,
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

const fillLines = (args: {
    origLines: LineInfo;
    actualScheme: ChildrenInfo;
}): LineInfo => {
    
    const { origLines, actualScheme } = args;
    let result: LineInfo = { items: [] };
    
    // Key is id of item, value is first visible parent (itself if element is visible)
    let visibilityOfItems: { [key: string]: ChildItem } = {};
    
    function walkChildrens(
        children: ChildItem[],
        visible: boolean,
        visibleParent: ChildItem
    ) {        
        children.forEach((c) => {
            visibilityOfItems[c.id] = visible ? c : visibleParent;
            if (c.children) {
                walkChildrens(
                    c.children,
                    visible && !(c.childrenCollapsed ?? DEFAULT_COLLAPSED),
                    visible ? c : visibleParent
                );
            }
        });
    }

    if (actualScheme.children) {
        walkChildrens(actualScheme.children, true, { id: "fakeRoot" });
    }

    type FoldedLineItem = {
        id: string;
        type?: string;
        src: string;
        dst: string;
        actualLines: LineItem[];
    };    
    // List to temprorary hold folded lines
    let foldedLines: FoldedLineItem[] = [];    
    origLines.items.forEach((line) => {
        const srcVisibility = visibilityOfItems[line.src];
        const dstVisibility = visibilityOfItems[line.dst];
        const srcVisible = line.src === srcVisibility.id;
        const dstVisible = line.dst === dstVisibility.id;
        if (srcVisible && dstVisible) {
            // All visible, just add to result
            result.items.push(line);
        } else {
            if (srcVisibility !== dstVisibility) {
                // Not "internal" line
                const foundFoldedLine = foldedLines.find(
                    (l) =>
                        l.src === srcVisibility.id &&
                        l.dst === dstVisibility.id &&
                        l.type === line.type
                );
                if (foundFoldedLine) {
                    foundFoldedLine.actualLines.push(line);
                } else {
                    foldedLines.push({
                        id: `gen_${srcVisibility.id}_${dstVisibility.id}_${
                            line.type ?? ""
                        }`,
                        src: srcVisibility.id,
                        dst: dstVisibility.id,
                        type: line.type,
                        actualLines: [line],
                    });
                }
            }
        }
    });
    
    foldedLines.forEach((l) => {
        result.items.push({
            id: l.id,
            src: l.src,
            dst: l.dst,
            type: l.type,
        });
    });
    
    return result;
};

export function useAnalyzeView({ name }: { name: string }) {
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<null | string>(null);
    const [data, setData] = useState<UniversalMapInfo | undefined>(undefined);
    const origLines = useRef<LineInfo>({ items: [] });

    async function fetchData() {
        setLoading(true);
        setError(null);

        try {            
            const response = await api.get<UniversalMapInfo>(`/api/analyzation/${name}`);
            origLines.current = response.data.lines;
            
            response.data.lines = fillLines({
                origLines: origLines.current,
                actualScheme: response.data.scheme,
            });

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

            // toogle collapsed
            const newData: ChildrenInfo = {
                children: toggleItemById(id, oldData.scheme.children ?? []),
                childrenLayout: oldData.scheme.childrenLayout,
            };

            return {
                lines: fillLines({
                    origLines: origLines.current,
                    actualScheme: newData,
                }),
                scheme: newData,
            };
        });
    }, []);

    return { loading, error, data, fetchData, toogleChildren };
}
