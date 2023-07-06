import { Center, useMantineTheme } from "@mantine/core";
import { INode } from "../core/models/IMap";
import { IconWorld } from "@tabler/icons-react";
import { MapSelection } from "./MapCommon";
import { useId } from '@mantine/hooks';


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

    const uuid = useId();

    return (
        <Center
            id={uuid}
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
