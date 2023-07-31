import React, { useState } from "react";
import UniversalMap from "../components/UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    findItemById,
    LayoutStyle,
} from "../components/UniversalMap/UniversalMapData";

import { HEADER_HEIGHT } from "../components/Header";
import { useMantineTheme } from "@mantine/core";

export function PolicyMap() {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";
    
    const styles: ItemStyles = {
        Cloud: {
            item: {
                style: {
                    margin: "2rem"
                }
            },
            header: {
                icon: "IconCloud",
            },
            layout: {
                childrenContainerStyle: {
                    border: "1px solid gray",
                    padding: "1rem",
                },
            },
        },
        VPC: {
            item: {
                style: {
                    margin: "0.5rem"
                }
            },
            header: {
                icon: "IconCloudFilled",
            },
            layout: {
                childrenContainerStyle: {
                    border: "1px solid gray",
                    padding: "1rem",
                },
            },
        },
        "Availability Zone": {
            item: {
                style: {
                    margin: "0.5rem"
                }
            },
            layout: {
                childrenContainerStyle: {
                    border: "1px solid gray",
                    padding: "1rem",
                },
            },
        },
        Subnet: {
            item: {
                style: {
                    margin: "0.5rem"
                }
            },
            header: {
                icon: "IconGridDots",
            },
            layout: {
                childrenContainerStyle: {
                    border: "1px solid gray",
                    padding: "1rem",
                },
            },
        },
        VM: {
            item: {
                style: {
                    border: "1px solid gray",
                    padding: "0.2rem",
                    background: isDark ? theme.colors.dark[6] : theme.colors.blue[3]
                }
            },
            header: {
                icon: "VM",
            },
        },
    };

    const initData: ChildrenInfo = {
        childrenLayout: "grid",
        children: [
            {
                id: "cloud-101",
                type: "Cloud",
                label: "Cloud Service 1",
                info: [
                    {
                        icon: "IconWorld",
                        tooltip: "This is Cloud Service 1",
                    },
                ],
                children: [
                    {
                        id: "vpc-201",
                        type: "VPC",
                        label: "VPC 1",
                        info: [
                            {
                                icon: "IconWorld",
                                tooltip: "This is VPC 1",
                            },
                            {
                                icon: "IconNetwork",
                                tooltip: "CIDR: 192.168.0.0/16",
                            },
                        ],
                        childrenLayout: "row",
                        children: [
                            {
                                id: "availability-zone-301",
                                type: "Availability Zone",
                                label: "Availability Zone A",
                                info: [
                                    {
                                        icon: "IconWorld",
                                        tooltip: "This is Availability Zone A",
                                    },
                                ],
                                childrenLayout: "grid",
                                children: [
                                    {
                                        id: "subnet-401",
                                        type: "Subnet",
                                        label: "Subnet 1",
                                        info: [
                                            {
                                                icon: "IconWorld",
                                                tooltip: "CIDR: 192.168.1.0/24",
                                            },
                                            {
                                                icon: "IconShield",
                                                tooltip:
                                                    "Private IP Addressing",
                                            },
                                            {
                                                icon: "IconCloudDownload",
                                                tooltip:
                                                    "Access: Internet Gateway",
                                            },
                                        ],
                                        childrenLayout: "column",
                                        children: [
                                            {
                                                id: "vm-501",
                                                type: "VM",
                                                label: "Virtual Machine 1",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.1.2",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                    {
                                                        icon: "IconGlobe",
                                                        tooltip:
                                                            "Public IP: 203.0.113.0",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-502",
                                                type: "VM",
                                                label: "Virtual Machine 2",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.1.3",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-601",
                                                type: "VM",
                                                label: "Virtual Machine 1.1",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.1.4",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                    {
                                                        icon: "IconGlobe",
                                                        tooltip:
                                                            "Public IP: 203.0.113.4",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-602",
                                                type: "VM",
                                                label: "Virtual Machine 1.2",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.1.5",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                    {
                                        id: "subnet-402",
                                        type: "Subnet",
                                        label: "Subnet 402",
                                        info: [
                                            {
                                                icon: "IconWorld",
                                                tooltip: "CIDR: 192.168.2.0/24",
                                            },
                                            {
                                                icon: "IconShield",
                                                tooltip:
                                                    "Private IP Addressing",
                                            },
                                            {
                                                icon: "IconCloudDownload",
                                                tooltip: "Access: NAT",
                                            },
                                        ],
                                        childrenLayout: "column",
                                        children: [
                                            {
                                                id: "vm-503",
                                                type: "VM",
                                                label: "Virtual Machine 3",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.2.2",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-504",
                                                type: "VM",
                                                label: "Virtual Machine 4",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.2.3",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                id: "availability-zone-302",
                                type: "Availability Zone",
                                label: "Availability Zone B",
                                info: [
                                    {
                                        icon: "IconWorld",
                                        tooltip: "This is Availability Zone B",
                                    },
                                ],
                                childrenLayout: "grid",
                                children: [
                                    {
                                        id: "subnet-403",
                                        type: "Subnet",
                                        label: "Subnet 3",
                                        info: [
                                            {
                                                icon: "IconWorld",
                                                tooltip: "CIDR: 192.168.3.0/24",
                                            },
                                            {
                                                icon: "IconShield",
                                                tooltip:
                                                    "Private IP Addressing",
                                            },
                                        ],
                                        childrenLayout: "column",
                                        children: [
                                            {
                                                id: "vm-505",
                                                type: "VM",
                                                label: "Virtual Machine 5",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.3.2",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-506",
                                                type: "VM",
                                                label: "Virtual Machine 6",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 192.168.3.3",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        id: "vpc-202",
                        type: "VPC",
                        label: "VPC 2",
                        info: [
                            {
                                icon: "IconWorld",
                                tooltip: "This is VPC 2",
                            },
                            {
                                icon: "IconNetwork",
                                tooltip: "CIDR: 10.0.0.0/16",
                            },
                        ],
                        childrenLayout: "row",
                        children: [
                            {
                                id: "availability-zone-303",
                                type: "Availability Zone",
                                label: "Availability Zone C",
                                info: [
                                    {
                                        icon: "IconWorld",
                                        tooltip: "This is Availability Zone C",
                                    },
                                ],
                                childrenLayout: "grid",
                                children: [
                                    {
                                        id: "subnet-404",
                                        type: "Subnet",
                                        label: "Subnet 4",
                                        info: [
                                            {
                                                icon: "IconWorld",
                                                tooltip: "CIDR: 10.0.1.0/24",
                                            },
                                            {
                                                icon: "IconShield",
                                                tooltip:
                                                    "Private IP Addressing",
                                            },
                                            {
                                                icon: "IconCloudDownload",
                                                tooltip:
                                                    "Access: Internet Gateway",
                                            },
                                        ],
                                        childrenLayout: "column",
                                        children: [
                                            {
                                                id: "vm-507",
                                                type: "VM",
                                                label: "Virtual Machine 7",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 10.0.1.2",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                    {
                                                        icon: "IconGlobe",
                                                        tooltip:
                                                            "Public IP: 203.0.113.1",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-508",
                                                type: "VM",
                                                label: "Virtual Machine 8",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 10.0.1.3",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                id: "cloud-102",
                type: "Cloud",
                label: "Cloud Service 2",
                info: [
                    {
                        icon: "IconWorld",
                        tooltip: "This is Cloud Service 2",
                    },
                ],
                children: [
                    {
                        id: "vpc-203",
                        type: "VPC",
                        label: "VPC 3",
                        info: [
                            {
                                icon: "IconWorld",
                                tooltip: "This is VPC 3",
                            },
                            {
                                icon: "IconNetwork",
                                tooltip: "CIDR: 172.16.0.0/16",
                            },
                        ],
                        childrenLayout: "row",
                        children: [
                            {
                                id: "availability-zone-304",
                                type: "Availability Zone",
                                label: "Availability Zone A",
                                info: [
                                    {
                                        icon: "IconWorld",
                                        tooltip: "This is Availability Zone A",
                                    },
                                ],
                                childrenLayout: "grid",
                                children: [
                                    {
                                        id: "subnet-405",
                                        type: "Subnet",
                                        label: "Subnet 5",
                                        info: [
                                            {
                                                icon: "IconWorld",
                                                tooltip: "CIDR: 172.16.1.0/24",
                                            },
                                            {
                                                icon: "IconShield",
                                                tooltip:
                                                    "Private IP Addressing",
                                            },
                                            {
                                                icon: "IconCloudDownload",
                                                tooltip:
                                                    "Access: Internet Gateway",
                                            },
                                        ],
                                        childrenLayout: "column",
                                        children: [
                                            {
                                                id: "vm-509",
                                                type: "VM",
                                                label: "Virtual Machine 9",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 172.16.1.2",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 2",
                                                    },
                                                    {
                                                        icon: "IconGlobe",
                                                        tooltip:
                                                            "Public IP: 203.0.113.2",
                                                    },
                                                ],
                                            },
                                            {
                                                id: "vm-510",
                                                type: "VM",
                                                label: "Virtual Machine 10",
                                                info: [
                                                    {
                                                        icon: "IconWorld",
                                                        tooltip:
                                                            "Private IP: 172.16.1.3",
                                                    },
                                                    {
                                                        icon: "IconCpu",
                                                        tooltip: "vCPU: 4",
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    };

    const [data, setData] = useState(initData);

    const toogleChildrens = function (id: string) {
        setData((oldData) => {
            const newData = JSON.parse(JSON.stringify(oldData));
            const item = findItemById(newData, id);
            if (item) {
                if (item.childrenCollapsed ?? false) {
                    item.childrenCollapsed = false;
                } else {
                    item.childrenCollapsed = true;
                }
            }
            return newData;
        });
    };

    const style: LayoutStyle = {
        horizontalGap: "5rem",
        verticalGap: "5rem",
    };

    return (
        <div
            style={{
                width: "100vw",
                height: `calc(100vh - ${HEADER_HEIGHT})`,
                position: "relative",
                backgroundColor: isDark ? theme.colors.gray[8] : "#F5F5DC",
            }}
        >
            <UniversalMap
                styles={styles}
                style={style}
                data={data}
                toogleChildrens={toogleChildrens}
            />
        </div>
    );
}
