import React, { useMemo } from "react";
import UniversalMap from "../components/UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    LayoutStyle,
} from "../components/UniversalMap/UniversalMapData";

import { useMantineTheme } from "@mantine/core";

interface PolicyMapViewProps {
    data: ChildrenInfo;
    selectedID?: string;
    toogleChildren?: (id: string) => void;
    select?: (id?: string) => void;
}

const PolicyMapView: React.FC<PolicyMapViewProps> = ({
        data,
        selectedID,
        toogleChildren,
        select
}) => {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

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

    const style: LayoutStyle = {
        horizontalGap: "5rem",
        verticalGap: "5rem",
        childrenContainerStyle: { margin: "5rem" },
    };

    return (
        <UniversalMap
                styles={styles}
                style={style}
                data={data}
                selectedID={selectedID}
                toogleChildren={toogleChildren}
                select={select}
            />
    );
}

export default PolicyMapView;