import {
    Box,
    Flex,
    MantineNumberSize,
    rem,
    useMantineTheme,
} from "@mantine/core";
import { DataType } from "csstype";
import React, { CSSProperties } from "react";
import { ReactNode } from "react";

interface MapGroupProps {
    id?: string;
    className?: string;
    groupTitle?: ReactNode;
    groupTitle2?: ReactNode;
    columnPolicy?: "column" | "row" | "squareRow" | "squareCol";
    borderLineStyle?: DataType.LineStyle;
    containerStyle?: CSSProperties;
    spacing?: MantineNumberSize;
    verticalSpacing?: MantineNumberSize;
    children?: ReactNode;
    borderColor?: string;
    textColor?: string;
}

export function MapGroup({
    id,
    className,
    groupTitle,
    groupTitle2,
    columnPolicy,
    borderLineStyle,
    containerStyle,
    spacing,
    verticalSpacing,
    children,
    borderColor,
    textColor,
    ...props
}: MapGroupProps) {
    const theme = useMantineTheme();
    const childrenCount = React.Children.count(children);

    if (!borderColor) {
        borderColor =
            theme.colorScheme === "dark" ? theme.colors.dark[0] : "black";
    }

    let cols = 0;
    if (columnPolicy === "column") {
        cols = 1;
    } else if (columnPolicy === "row") {
        cols = childrenCount;
    } else {
        cols = Math.sqrt(childrenCount);
        if (!Number.isInteger(cols)) {
            cols = Math.floor(cols);
            if (columnPolicy === "squareRow") {
                cols += 1; // prefer more columns
            }
        }
    }

    const rows = Math.ceil(childrenCount / cols);
    const childComponents: ReactNode[] = [];
    const childrenArray = React.Children.toArray(children);
    let index = 0;

    for (let row = 0; row < rows; row++) {
        const flexChildren: ReactNode[] = [];

        for (let col = 0; col < cols; col++) {
            if (index < childrenCount) {
                flexChildren.push(childrenArray[index]);
                index++;
            } else {
                break;
            }
        }

        childComponents.push(
            <Flex key={row} gap={spacing ?? "1rem"} align="center">
                {flexChildren}
            </Flex>
        );
    }

    return (
        <div id={id} style={containerStyle} className={className} {...props}>
            {(groupTitle || groupTitle2) && (
                <Box style={{ display: "flex", color: textColor }}>
                    <div
                        style={{
                            position: "relative",
                            overflow: "hidden",
                            flex: 1,
                        }}
                    >
                        <Box
                            style={{
                                position: "absolute",
                                whiteSpace: "nowrap",
                                textOverflow: "ellipsis"                                
                            }}
                        >
                            {groupTitle}
                        </Box>
                    </div>
                    {groupTitle2 && <Box pl={"0.5rem"}>{groupTitle2}</Box>}
                </Box>
            )}
            <Flex
                direction="column"
                p="1.5rem"
                gap={verticalSpacing ?? "1rem"}
                align="center"
                sx={{
                    border: `${rem(1)} ${
                        borderLineStyle ?? "solid"
                    } ${borderColor}`,
                }}
            >
                {childComponents}
            </Flex>
        </div>
    );
}
