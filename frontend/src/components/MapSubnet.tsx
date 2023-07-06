import { Flex, useMantineTheme } from "@mantine/core";
import React from "react";
import { MapGroup } from "./MapGroup";
import { IconNetwork } from "@tabler/icons-react";
import { ISubnet } from "../core/models/IMap";
import { MapVM } from "./MapVM";
import { MapSelection } from "./MapCommon";


interface MapSubnetProps {
    subnet: ISubnet;
    selection?: MapSelection;
}

export function MapSubnet({ subnet, selection }: MapSubnetProps) {
    const isSelected = selection && selection.type === "subnet" && Number(selection.key) === subnet.id;

    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

    let textColor: string | undefined = undefined;
    let borderColor: string | undefined = undefined;

    if (isDark) {
        textColor = isSelected ? theme.colors.blue[6] : undefined;
        borderColor = isSelected ? theme.colors.blue[6] : undefined;
    }
    else {
        textColor = isSelected ? "blue" : undefined;
        borderColor = isSelected ? "blue" : undefined;
    }

    return (
        <MapGroup
            id={`map_subnet${subnet.id}`}
            className="map-subnet"
            data-id={subnet.id}
            groupTitle={
                <Flex gap="0.1rem">
                    <IconNetwork /> {subnet.name}
                </Flex>
            }
            groupTitle2={subnet.cidr}
            borderLineStyle="dashed"
            
            columnPolicy="squareRow"
            containerStyle={{ minWidth: "20rem" }}
            textColor={textColor}
            borderColor={borderColor}
        >
            {subnet.vms.map((vm) => (
                <MapVM key={vm.id} vm={vm} selection={selection} />
            ))}
        </MapGroup>
    );
}
