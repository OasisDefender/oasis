import React, { forwardRef, useRef } from "react";
import * as TablerIcons from "@tabler/icons-react";
import { Tooltip } from "@mantine/core";

interface UniversalIconProps {
    name: string;
    color?: string;
    tooltip?: string;
}

const UniversalIcon = ({ name, color, tooltip }: UniversalIconProps) => {
    const ref = useRef<HTMLDivElement>(null);
    let icon;
    if (name.startsWith("Icon") && name.length > 4 && name in TablerIcons) {
        //@ts-ignore
        const IconComponent = TablerIcons[name];
        icon = <IconComponent color={color} ref={ref}/>;
    } else {
        icon = (
            <div
                ref={ref}
                style={{
                    border: `2px solid ${color ?? ""}`,
                    color: color ?? undefined,
                    lineHeight: 1,
                    padding: "2px",
                    margin: "2px",
                    fontWeight: 600,
                    borderRadius: "20%",
                }}
            >
                {name}
            </div>
        );
    }
    if (tooltip) {
        return (
            <Tooltip label={tooltip} withArrow withinPortal>
                {icon}
            </Tooltip>
        );
    } else {
        return icon;
    }    
};

export default UniversalIcon;
