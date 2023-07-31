import React, { forwardRef } from "react";
import * as TablerIcons from "@tabler/icons-react";

interface UniversalIconProps {
  name: string;
  color?: string;
}

const UniversalIcon = forwardRef<HTMLDivElement, UniversalIconProps>(
  ({ name, color }, ref) => {
    if (name.startsWith("Icon") && name.length > 4 && name in TablerIcons) {
      //@ts-ignore
      const IconComponent = TablerIcons[name];    
      return <IconComponent color={color} ref={ref} />;
    }
    return <div style={{
      border: `2px solid ${color ?? ""}`,
      color: color ?? undefined,
      lineHeight: 1,
      padding: "2px",
      margin: "2px",
      fontWeight: 600,
      borderRadius: "20%"
    }}>{name}</div>    
  }
);

export default UniversalIcon;
