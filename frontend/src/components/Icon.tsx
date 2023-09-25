import React from "react";
import { Text, Flex, useMantineTheme, rem } from "@mantine/core";

interface IconProps extends React.ComponentPropsWithoutRef<"svg"> {
    size?: number | string;
    inverted?: boolean;
    iconTextClasses?: string;
}

export function Icon({
    size,
    inverted,
    iconTextClasses,
    ...others
}: IconProps) {
    const theme = useMantineTheme();

    return (
        <Flex justify="center" align="center" gap="xs">
            <svg
                style={{ display: "inline" }}
                {...others}
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 3458.7 2980.23"
                height={rem(size)}
            >
                <defs>
                    <linearGradient
                        id="id0"
                        gradientUnits="userSpaceOnUse"
                        x1="-0"
                        y1="1490.12"
                        x2="3458.7"
                        y2="1490.12"
                    >
                        <stop offset="0" stopOpacity={1} stopColor="#02949D" />
                        <stop
                            offset="0.45098"
                            stopOpacity={1}
                            stopColor="#8DDCE0"
                        />
                        <stop offset="1" stopOpacity={1} stopColor="#3EBCC1" />
                    </linearGradient>
                </defs>
                <g fill="none" fillRule="evenodd">
                    <polygon
                        fill="url(#id0)"
                        points="3458.7,2980.23 -0,2980.23 220.17,2600.08 2791.16,2600.08 1730.16,766.03 885.08,2223.29 436.27,2223.29 1730.16,0 "
                    />                                       
                </g>
            </svg>
            <Text
                fz="lg"
                sx={{
                    fontFamily:
                        'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
                }}
                className={iconTextClasses}
            >
                Oasis Defender
            </Text>
        </Flex>
    );
}
