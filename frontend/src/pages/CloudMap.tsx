import React, { ReactNode, useEffect, useState } from "react";
import {
    PressEventCoordinates,
    PressHandlingOptions,
    Space as ZoomSpace,
} from "react-zoomable-ui";

import { HEADER_HEIGHT } from "../components/Header";
import {
    Alert,
    Button,
    Loader,
    LoadingOverlay,
    Modal,
    px,
    useMantineTheme,
} from "@mantine/core";
import { MapVPC } from "../components/MapVPC";
import { useMap } from "../core/hooks/map";
import { MapGroup } from "../components/MapGroup";
import { IconAlertTriangle, IconPlus } from "@tabler/icons-react";
import { useDisclosure } from "@mantine/hooks";
import { AddTargetForm } from "../components/AddTargetForm";
import { MapSelection } from "../components/MapCommon";
import { MapNetwork } from "../components/MapNetwork";
import { MapLines } from "../components/MapLines";
import { ILink } from "../core/models/ILinks";
import { ShowModalError } from "../core/oasiserror";
import { AxiosError } from "axios";
import { useXarrow } from "react-xarrows";

export function CloudMap() {
    const theme = useMantineTheme();
    const dark = theme.colorScheme === "dark";
    const spaceRef = React.useRef<ZoomSpace | null>(null);
    const innerDivRef = React.useRef<HTMLDivElement | null>(null);
    const { loading: mapLoading, error, themap, addTarget, getLinksVM } = useMap();
    const [loading, setLoading] = useState(false);
    const [lines, setLines] = useState<ILink[]>([]);
    const [selectedLineIndex, setSelectedLineIndex] = useState<number>(-1);
    const [zoomFactor, setZoomFactor] = useState(1);
    const refreshLines = useXarrow();

    // Selection
    const [selection, setSelection] = useState<MapSelection | undefined>(
        undefined
    );
    
    useEffect(() => {
        const fetchData = async () => {            
            if (selection && selection.type === "vm") {
                setLoading(true);
                try {
                    const res = await getLinksVM(Number(selection.key));
                    console.log("res", res);
                    setLines(res.links);
                } catch (e: unknown) {                
                    ShowModalError(`Error while getting links for VM`, e as AxiosError);
                }
                setLoading(false);
            }
        }        
        fetchData();
    }, [selection]);

    // Target add
    const [
        addTargetModalOpened,
        { open: openAddTargetModal, close: closeAddTargetModal },
    ] = useDisclosure(false);
    async function addTargetAndClose({ target }: { target: string }) {
        await addTarget({ target });
        closeAddTargetModal();
    }
    async function onAddTargetClick(
        e: React.MouseEvent<HTMLButtonElement, MouseEvent>
    ) {
        e.stopPropagation();
        openAddTargetModal();
    }

    useEffect(() => {
        const moveToCenter = () => {
            if (themap && spaceRef.current && innerDivRef.current) {
                spaceRef.current.viewPort?.camera.centerFitElementIntoView(
                    innerDivRef.current,
                    {
                        elementExtraMarginForZoomInClientSpace: px("2rem"),
                    },
                    {
                        durationMilliseconds: 1000,
                    }
                );
            } else if (themap) {
                // wait spaceRef and innerDivRef will render
                setTimeout(moveToCenter, 25);
            }
        };

        moveToCenter();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [themap?.vpcs]);


    function onDecideHowToHandlePress(
        e: MouseEvent | TouchEvent,
        coordinates: PressEventCoordinates
    ): PressHandlingOptions | undefined {
        if (e.target && e.target instanceof Element) {
            if (e.target.closest("button")) {
                return { ignorePressEntirely: true };
            }

            const arrow = e.target.closest(".map-arrow");
            if (arrow) {
                return {
                    onTap() {
                        setSelectedLineIndex(Number(arrow.getAttribute("data")));
                    },
                };
            }

            const item = e.target.closest(
                ".map-vpc, .map-subnet, .map-vm, .map-network"
            );
            if (item) {
                let type: "vpc" | "subnet" | "vm" | "network" | null = null;
                const id = item.getAttribute("data-id");

                if (item.classList.contains("map-vpc")) {
                    type = "vpc";
                } else if (item.classList.contains("map-subnet")) {
                    type = "subnet";
                } else if (item.classList.contains("map-vm")) {
                    type = "vm";
                } else if (item.classList.contains("map-network")) {
                    type = "network";
                }

                if (type && id) {
                    const selection: MapSelection = {
                        type: type,
                        key: id,
                    };
                    return {
                        onTap() {
                            setSelectedLineIndex(-1);
                            setLines([]);                            
                            setSelection(selection);
                        },
                    };
                }
            }
        }
        return {
            onTap() {
                if (selectedLineIndex >= 0) {
                    setSelectedLineIndex(-1);
                }
                else {
                    setLines([]);
                    setSelection(undefined);
                }
            },
        };
    }

    let content: ReactNode | null = null;
    if (mapLoading) {
        content = (
            <Loader
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                }}
            />
        );
    } else if (error || !themap) {
        content = (
            <Alert
                icon={<IconAlertTriangle size="1rem" />}
                title="Cannot get the map"
                color="red"
                mt={"xs"}
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                }}
            >
                {error}
            </Alert>
        );
    } else {
        content = (            
            <ZoomSpace
                ref={spaceRef}
                onCreate={(viewPort) => {
                    viewPort.camera.moveBy(
                        -document.documentElement.clientWidth,
                        -document.documentElement.clientHeight
                    );
                }}
                onDecideHowToHandlePress={onDecideHowToHandlePress}
                onUpdated={(ViewPort) => {
                    setZoomFactor(ViewPort.zoomFactor);
                    setTimeout(refreshLines, 0);
                }}
            >
                <div style={{ position: "absolute" }} ref={innerDivRef}>
                    <MapGroup
                        borderLineStyle="none"
                        columnPolicy="squareRow"
                        spacing="5rem"
                        verticalSpacing="5rem"
                    >
                        {themap.vpcs.map((vpc) => (
                            <MapVPC
                                key={vpc.id}
                                vpc={vpc}
                                selection={selection}
                            />
                        ))}
                    </MapGroup>
                    <MapGroup borderLineStyle="none" columnPolicy="row">
                        {themap.inodes.map((node) => (
                            <MapNetwork
                                key={node}
                                node={node}
                                selection={selection}
                            />
                        ))}
                        <Button
                            variant="subtle"
                            color={dark ? "white" : "dark"}
                            compact
                            onClick={onAddTargetClick}
                        >
                            <IconPlus /> Add target
                        </Button>
                    </MapGroup>
                    <MapLines from={selection} lines={lines} zoomFactor={zoomFactor} selectedIndex={selectedLineIndex} />
                </div>                 
            </ZoomSpace>            
        );
    }
    return (
        <>
            <div
                style={{
                    width: "100vw",
                    height: `calc(100vh - ${HEADER_HEIGHT})`,
                    position: "relative",
                    backgroundColor: dark ? theme.colors.gray[8] : "#F5F5DC",
                }}
            >
                {content}
            </div>
            <Modal
                opened={addTargetModalOpened}
                onClose={closeAddTargetModal}
                title="Add target"
                centered
            >
                <AddTargetForm
                    onCancel={closeAddTargetModal}
                    makeAddTarget={addTargetAndClose}
                />
            </Modal>
            <LoadingOverlay visible={loading} transitionDuration={500} style={{pointerEvents: "none"}} />
        </>
    );
}
