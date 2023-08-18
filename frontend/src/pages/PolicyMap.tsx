import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import UniversalMap from "../components/UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    findItemById,
    LayoutStyle,
    DEFAULT_COLLAPSED,
    LineInfo,
    LineStyles,
    ChildItem,
    findItemAndParentsById,
} from "../components/UniversalMap/UniversalMapData";

import { HEADER_HEIGHT } from "../components/Header";
import { useMantineTheme } from "@mantine/core";

export function PolicyMap() {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";
    const [selected, setSelected] = useState<string | undefined>(undefined);
    const [selectedLine, setSelectedLine] = useState<string | undefined>(
        undefined
    );
    const selectedRef = useRef(selected);
    const selectedLineRef = useRef(selected);

    useEffect(() => {
        selectedRef.current = selected;
        selectedLineRef.current = selectedLine;
    }, [selected, selectedLine]);

    const select = (id: string | undefined) => {
        if (selectedLineRef.current) {
            setSelectedLine(undefined);
        }
        setSelected(id);
    };
    const selectLine = (id: string | undefined) => {
        if (selectedRef.current) {
            setSelected(undefined);
        }
        setSelectedLine(id);
    };

    const styles: ItemStyles = useMemo(() => {
        return {
            Cloud: {
                item: {
                    style: {
                        margin: "2rem",
                    },
                },
                header: {
                    icon: "IconCloud",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            VPC: {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                header: {
                    icon: "IconCloudFilled",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            "Availability Zone": {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            Subnet: {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                header: {
                    icon: "IconGridDots",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            VM: {
                item: {
                    style: {
                        border: "1px solid gray",
                        padding: "0.2rem",
                        background: isDark
                            ? theme.colors.dark[6]
                            : theme.colors.blue[3],
                    },
                },
                itemSelected: {
                    style: {
                        background: isDark ? theme.colors.gray[0] : "white",
                    },
                },
                header: {
                    icon: "VM",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
            },
        };
    }, [isDark]);

    function randomChildCount(): number {
        return Math.floor(Math.random() * 10) + 1;
    }

    function generateMockVM(prevID: string, id: number): ChildItem {
        return {
            id: `vm-${prevID}-${id}`,
            type: "VM",
            label: `Virtual Machine ${id}`,
            info: [
                {
                    icon: "IconWorld",
                    tooltip: `Private IP: 192.168.${id}.${id}`,
                },
                {
                    icon: "IconCpu",
                    tooltip: `vCPU: ${2 * ((id % 2) + 1)}`, // alternating between 2 and 4 vCPUs
                },
            ],
        };
    }

    function generateMockSubnet(
        prevID: string,
        id: number,
        childCount = randomChildCount()
    ): ChildItem {
        const vms: ChildItem[] = [];
        for (let i = 0; i < childCount; i++) {
            vms.push(generateMockVM(`${prevID}-${id}`, i));
        }
        return {
            id: `subnet-${prevID}-${id}`,
            type: "Subnet",
            label: `Subnet ${id}`,
            info: [
                {
                    icon: "IconWorld",
                    tooltip: `CIDR: 192.168.${id}.0/24`,
                },
                {
                    icon: "IconShield",
                    tooltip: "Private IP Addressing",
                },
                {
                    icon: "IconCloudDownload",
                    tooltip:
                        id % 2 === 0
                            ? "Access: Internet Gateway"
                            : "Access: NAT", // alternate for mock
                },
            ],
            childrenLayout: "grid",
            children: vms,
        };
    }

    function generateMockAZ(
        prevID: string,
        id: number,
        childCount = randomChildCount()
    ): ChildItem {
        const subnets: ChildItem[] = [];
        for (let i = 0; i < childCount; i++) {
            subnets.push(generateMockSubnet(`${prevID}-${id}`, i));
        }
        return {
            id: `availability-zone-${prevID}-${id}`,
            type: "Availability Zone",
            label: `Availability Zone ${id}`,
            info: [
                {
                    icon: "IconWorld",
                    tooltip: `This is Availability Zone ${id}`,
                },
            ],
            childrenLayout: "grid",
            children: subnets,
        };
    }

    function generateMockVPC(
        prevID: string,
        id: number,
        childCount = randomChildCount()
    ): ChildItem {
        const azs: ChildItem[] = [];
        for (let i = 0; i < childCount; i++) {
            azs.push(generateMockAZ(`${prevID}-${id}`, i));
        }
        return {
            id: `vpc-${prevID}-${id}`,
            type: "VPC",
            label: `VPC ${id}`,
            info: [
                {
                    icon: "IconWorld",
                    tooltip: `This is VPC ${id}`,
                },
            ],
            childrenLayout: "grid",
            children: azs,
        };
    }

    function generateMockCloud(
        prevID: string,
        id: number,
        childCount = randomChildCount()
    ): ChildItem {
        const vpcs: ChildItem[] = [];
        for (let i = 0; i < childCount; i++) {
            vpcs.push(generateMockVPC(`${prevID}-${id}`, i));
        }
        return {
            id: `cloud-${prevID}-${id}`,
            type: "Cloud",
            label: `Cloud Service ${id}`,
            info: [
                {
                    icon: "IconWorld",
                    tooltip: `This is Cloud Service ${id}`,
                },
            ],
            childrenLayout: "grid",
            children: vpcs,
        };
    }

    const initData: ChildrenInfo = {
        childrenLayout: "grid",
        children: [
            generateMockCloud("", 1),
            generateMockCloud("", 2),
            generateMockCloud("", 3),
        ],
    };

    const initLines: LineInfo = {
        items: [
            {
                src: "vm-509",
                dst: "vm-510",
                srcTooltip: "Label srcTooltip",
                dstTooltip: "Label dstTooltip",
            },
            {
                src: "vm-509",
                dst: "availability-zone-301",
                srcTooltip: "Label srcTooltip",
                dstTooltip: "Label dstTooltip",
            },
            {
                src: "vm-510",
                dst: "availability-zone-301",
                srcTooltip: "Label srcTooltip",
                dstTooltip: "Label dstTooltip",
            },
            {
                src: "vm-601",
                dst: "availability-zone-301",
                srcTooltip: "Label srcTooltip",
                dstTooltip: "Label dstTooltip",
            },
            {
                src: "vm-601",
                dst: "vm-601",
                srcTooltip: "Label srcTooltip",
                dstTooltip: "Label dstTooltip",
            },
        ],
    };

    const lineStyles: LineStyles = {
        "": {
            line: {
                stroke: "gray",
            },
            lineSelected: {
                stroke: "cornflowerblue",
                strokeOpacity: 1,
            },
        },
    };

    const [data, setData] = useState(initData);

    const toggleItemById = (id: string, items: ChildItem[]): ChildItem[] => {
        let changed = false;
    
        const updatedItems = items.map(item => {
            if (item.id === id) {
                changed = true;
                return {
                    ...item,
                    childrenCollapsed: !(item.childrenCollapsed ?? DEFAULT_COLLAPSED)
                };
            }
            
            if (item.children) {
                const updatedChildren = toggleItemById(id, item.children);
                if (updatedChildren !== item.children) {
                    changed = true;
                    return {
                        ...item,
                        children: updatedChildren
                    };
                }
            }
            
            return item;
        });
    
        return changed ? updatedItems : items;
    };
    
    const toogleChildren = useCallback((id: string) => {
        setData((oldData) => {
            const newData : ChildrenInfo = {
                children: toggleItemById(id, oldData.children ?? []),
                childrenLayout: oldData.childrenLayout
            };
            return newData;
        });
    }, []);

    const style: LayoutStyle = {
        horizontalGap: "5rem",
        verticalGap: "5rem",
        childrenContainerStyle: { margin: "5rem" },
    };

    const [lines, setLines] = useState(initLines);

    return (
        <div
            style={{
                width: "100vw",
                height: `calc(100vh - ${HEADER_HEIGHT})`,
                position: "relative",
                backgroundColor: isDark ? theme.colors.gray[8] : "#F5F5DC",
                overflow: "hidden",
            }}
        >
            <UniversalMap
                styles={styles}
                lineStyles={lineStyles}
                style={style}
                data={data}
                lines={lines}
                selectedID={selected}
                selectedLineID={selectedLine}
                toogleChildren={toogleChildren}
                select={select}
                selectLine={selectLine}
            />
        </div>
    );
}
