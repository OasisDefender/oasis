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
import { severityToHeaderBGColor, severityToLineColor } from "../core/severity";

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
        const getCloudStyle = (bg: string | undefined) => {
            return {
                item: {
                    style: {
                        margin: "2rem",
                        background: bg,
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
            };
        };

        const getVMStyle = (bg: string | undefined) => {
            return {
                item: {
                    style: {
                        border: "1px solid gray",
                        padding: "0.2rem",
                        background:
                            bg ??
                            (isDark
                                ? theme.colors.dark[6]
                                : theme.colors.blue[3]),
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
            "Cloud0": getCloudStyle(undefined),
            "Cloud1": getCloudStyle(severityToHeaderBGColor(1)),
            "Cloud2": getCloudStyle(severityToHeaderBGColor(2)),
            "Cloud3": getCloudStyle(severityToHeaderBGColor(3)),
            "VM0": getVMStyle(undefined),
            "VM1": getVMStyle(severityToHeaderBGColor(1)),
            "VM2": getVMStyle(severityToHeaderBGColor(2)),
            "VM3": getVMStyle(severityToHeaderBGColor(3))
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
            "line0": getLineStyle(isDark ? "#FFFFFF80" : "#00000040"),
            "line1": getLineStyle(severityToLineColor(1)),            
            "line2": getLineStyle(severityToLineColor(2)),
            "line3": getLineStyle(severityToLineColor(3)),
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
