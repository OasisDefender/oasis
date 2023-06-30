import { Center, useMantineTheme } from "@mantine/core";
import { INode } from "../core/models/IMap";
import { IconWorld } from "@tabler/icons-react";
import { MapSelection } from "./MapCommon";

interface MapNetworkProps {
    node: INode;
    selection?: MapSelection;
}

export function MapNetwork({ node, selection }: MapNetworkProps) {
    const isSelected =
        selection && selection.type === "network" && selection.key === node;

    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

    let textColor: string | undefined = undefined;

    if (isDark) {
        textColor = isSelected ? theme.colors.blue[6] : undefined;
    }
    else {
        textColor = isSelected ? "blue" : undefined;
    }

    return (
        <Center
            className="map-network"
            data-id={node}
            key={node}
            sx = {{
                color: textColor
            }}            
        >
            <IconWorld /> {node}
        </Center>
    );
}
