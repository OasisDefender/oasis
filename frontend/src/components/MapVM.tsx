import { Box, Flex, Tooltip, rem, useMantineTheme } from "@mantine/core";
import { IconWorld } from "@tabler/icons-react";
import { IVM } from "../core/models/IMap";
import { MapSelection } from "./MapCommon";

interface MapVMProps {
    vm: IVM;
    selection?: MapSelection;
}

export function MapVM({ vm, selection }: MapVMProps) {
    const isSelected =
        selection && selection.type === "vm" && Number(selection.key) === vm.id;

    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

    let textColor: string | undefined = undefined;
    let bgColor: string | undefined = undefined;
    let borderColor: string | undefined = undefined;
    let hoverBgColor: string | undefined = undefined;    

    if (isDark) {
        textColor = isSelected ? theme.colors.blue[6] : undefined;
        bgColor = isSelected ? theme.colors.gray[0] : theme.colors.dark[6];
        hoverBgColor = isSelected ? undefined : theme.colors.dark[4];
        borderColor = theme.colors.dark[0];
    } else {
        textColor = isSelected ? "blue" : undefined;
        bgColor = isSelected ? "white" : theme.colors.blue[3];
        hoverBgColor = isSelected ? undefined : theme.colors.blue[2];
        borderColor = "black";
    }

    return (
        <Flex
            id={`map_vm${vm.id}`}
            className="map-vm"            
            data-id={vm.id}
            bg={bgColor}
            gap="xs"
            justify="center"
            align="center"
            direction="row"
            pr="0.5rem"
            pl="0.5rem"
            miw="5rem"
            sx={{
                border: `${rem(1)} solid ${borderColor}`,
                cursor: "pointer",
                "&:hover": {
                    backgroundColor: hoverBgColor,
                },
            }}
        >
            <Box maw={"10rem"} sx={{
                color: textColor,
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                overflow: "hidden"
            }}>
                {vm.name} 
            </Box>
            {vm.publicIP ? (
                <Tooltip label={vm.publicIP} withArrow withinPortal>
                    <IconWorld color={textColor} />
                </Tooltip>
            ) : (
                false
            )}
        </Flex>
    );
}
