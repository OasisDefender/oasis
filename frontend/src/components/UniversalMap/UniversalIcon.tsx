import React, { forwardRef } from "react";
import { Badge } from "@mantine/core";
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

    return <Badge color={color} radius="xs" variant="outline" ref={ref}>{name}</Badge>;
  }
);

export default UniversalIcon;
