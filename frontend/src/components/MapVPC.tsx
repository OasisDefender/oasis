import { Flex, useMantineTheme } from "@mantine/core";
import React from "react";
import { MapGroup } from "./MapGroup";
import { IconCloudFilled } from "@tabler/icons-react";
import { IVPC } from "../core/models/IMap";
import { MapSubnet } from "./MapSubnet";
import { MapSelection } from "./MapCommon";


interface MapVPCProps {
    vpc: IVPC;
    selection?: MapSelection;
}

export function MapVPC({ vpc, selection }: MapVPCProps) {
    const isSelected = selection && selection.type === "vpc" && Number(selection.key) === vpc.id;

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
            id={`map_vpc${vpc.id}`}
            className="map-vpc"
            data-id={vpc.id}
            groupTitle={
                <Flex gap="0.1rem">
                    <IconCloudFilled /> {vpc.name}
                </Flex>
            }
            groupTitle2={vpc.cidr}
            borderLineStyle="dashed"
            columnPolicy="squareCol"
            containerStyle={{ minWidth: "20rem" }}
            borderColor={borderColor}
            textColor={textColor}
        >
            {vpc.subnets.map((subnet) => (
                <MapSubnet
                    key={subnet.id}
                    subnet={subnet}
                    selection={selection}
                />
            ))}
        </MapGroup>
    );
}
