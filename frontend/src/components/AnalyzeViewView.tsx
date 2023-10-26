import React, { useMemo } from "react";
import UniversalMap from "./UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    LayoutStyle,
    LineInfo,
    LineStyles,
} from "./UniversalMap/UniversalMapData";

import { useMantineTheme } from "@mantine/core";
import { severityToColor } from "../core/severity";

interface PolicyMapViewProps {
    data: ChildrenInfo;
    lines: LineInfo;
    selectedID?: string;
    toogleChildren?: (id: string) => void;
    select?: (id?: string) => void;
}

const AnalyzeViewView: React.FC<PolicyMapViewProps> = ({
    data,
    lines,
    selectedID,
    toogleChildren,
    select,
}) => {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

    const styles: ItemStyles = useMemo(() => {
        const getCloudStyle = (bg?: string) => {
            return {
                item: {
                    style: {
                        margin: "2rem",                        
                    },                    
                },
                header: {
                    icon: "IconCloud",
                    style: {
                        borderBottom: bg ? `10px solid ${bg}` : undefined
                    }                  
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
            };
        };

        const getSubnetStyle = (bg: string | undefined) => {
            return {
                item: {
                    style: {
                        margin: "0.5rem"                        
                    },
                },
                header: {
                    icon: "IconGridDots",
                    style: {
                        borderBottom: bg ? `10px solid ${bg}` : undefined
                    }
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                    horizontalGap: "3rem",
                    verticalGap: "3rem",
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            };
        };

        const getVMStyle = (bg: string | undefined) => {
            return {
                item: {
                    style: {
                        border: "2px solid gray",
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
                    maxLabelWidth: "15rem",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
            };
        };

        return {
            "Cloud0": getCloudStyle(severityToColor(0)),
            "Cloud1": getCloudStyle(severityToColor(1)),
            "Cloud2": getCloudStyle(severityToColor(2)),
            "Cloud3": getCloudStyle(severityToColor(3)),
            "Subnet0": getSubnetStyle(severityToColor(0)),
            "Subnet1": getSubnetStyle(severityToColor(1)),
            "Subnet2": getSubnetStyle(severityToColor(2)),
            "Subnet3": getSubnetStyle(severityToColor(3)),
            "VM0": getVMStyle(severityToColor(0)),
            "VM1": getVMStyle(severityToColor(1)),
            "VM2": getVMStyle(severityToColor(2)),
            "VM3": getVMStyle(severityToColor(3))
        };
    }, [isDark]);

    const lineStyles: LineStyles = useMemo(() => {
        const getLineStyle = (color: string | undefined) => {
            return {
                line: {
                    stroke: color,
                    strokeOpacity: 0.6
                }
            }
        };

        return {
            "line0": getLineStyle(severityToColor(0)),
            "line1": getLineStyle(severityToColor(1)),            
            "line2": getLineStyle(severityToColor(2)),
            "line3": getLineStyle(severityToColor(3)),
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
            lineStyles={lineStyles}
            style={style}
            data={data}
            lines={lines}
            selectedID={selectedID}
            toogleChildren={toogleChildren}
            select={select}
        />
    );
};

export default AnalyzeViewView;
