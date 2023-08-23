import React, {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";
import UniversalMap from "../components/UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    LayoutStyle,
    DEFAULT_COLLAPSED,
    ChildItem,
} from "../components/UniversalMap/UniversalMapData";

import { HEADER_HEIGHT } from "../components/Header";
import {
    Alert,
    Button,
    Loader,
    ScrollArea,
    useMantineTheme,
} from "@mantine/core";
import PolicyMapFilters from "../components/PolicyMapFilters";
import { useClassifiers } from "../core/hooks/classifiers";
import { IconAlertTriangle } from "@tabler/icons-react";
import { usePolicyMap } from "../core/hooks/policymap";
import PolicyMapView from "../components/PolicyMapView";

export function PolicyMap() {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";
    const [selected, setSelected] = useState<string | undefined>(undefined);
    const [stage, setStage] = useState<"filters" | "view">("filters");
    const {
        loading: classifiersLoading,
        error: classifiersError,
        data: classifiers,
    } = useClassifiers();
    const {
        loading: classificationLoading,
        error: classificationError,
        data: classification,
        fetchData: fetchClassification,
    } = usePolicyMap();

    const selectedRef = useRef(selected);

    useEffect(() => {
        selectedRef.current = selected;
    }, [selected]);

    const select = (id: string | undefined) => {
        setSelected(id);
    };

    const styles: ItemStyles = useMemo(() => {
        return {
            Cloud: {
                item: {
                    style: {
                        margin: "2rem",
                    },
                },
                header: {
                    icon: "IconCloud",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            VPC: {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                header: {
                    icon: "IconCloudFilled",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            "Availability Zone": {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            Subnet: {
                item: {
                    style: {
                        margin: "0.5rem",
                    },
                },
                header: {
                    icon: "IconGridDots",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
                layout: {
                    childrenContainerStyle: {
                        border: "1px solid gray",
                        padding: "1rem",
                    },
                },
                layoutSelected: {
                    childrenContainerStyle: {
                        border: `1px solid ${
                            isDark ? theme.colors.blue[6] : "blue"
                        }`,
                    },
                },
            },
            VM: {
                item: {
                    style: {
                        border: "1px solid gray",
                        padding: "0.2rem",
                        background: isDark
                            ? theme.colors.dark[6]
                            : theme.colors.blue[3],
                    },
                },
                itemSelected: {
                    style: {
                        background: isDark ? theme.colors.gray[0] : "white",
                    },
                },
                header: {
                    icon: "VM",
                },
                headerSelected: {
                    textColor: isDark ? theme.colors.blue[6] : "blue",
                },
            },
        };
    }, [isDark]);

    const [data, setData] = useState<ChildrenInfo>({});

    const toggleItemById = (id: string, items: ChildItem[]): ChildItem[] => {
        let changed = false;

        const updatedItems = items.map((item) => {
            if (item.id === id) {
                changed = true;
                return {
                    ...item,
                    childrenCollapsed: !(
                        item.childrenCollapsed ?? DEFAULT_COLLAPSED
                    ),
                };
            }

            if (item.children) {
                const updatedChildren = toggleItemById(id, item.children);
                if (updatedChildren !== item.children) {
                    changed = true;
                    return {
                        ...item,
                        children: updatedChildren,
                    };
                }
            }

            return item;
        });

        return changed ? updatedItems : items;
    };

    const toogleChildren = useCallback((id: string) => {
        setData((oldData) => {
            const newData: ChildrenInfo = {
                children: toggleItemById(id, oldData.children ?? []),
                childrenLayout: oldData.childrenLayout,
            };
            return newData;
        });
    }, []);

    const style: LayoutStyle = {
        horizontalGap: "5rem",
        verticalGap: "5rem",
        childrenContainerStyle: { margin: "5rem" },
    };

    const showData = (classifiersIds: number[]) => {
        console.log("fetchClassification", classifiersIds);
        fetchClassification(classifiersIds);
        setStage("view");
        console.log(classification);
    };

    let content: React.ReactNode = <></>;
    const getLoader = () => (
        <Loader
            sx={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
            }}
        />
    );
    const getError = (error: string) => (
        <ScrollArea
            h="100%"
            type="auto"
            offsetScrollbars
            pt="1rem"
            sx={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
            }}
        >
            <Alert
                icon={<IconAlertTriangle size="1rem" />}
                title="Cannot get classifiers"
                color="red"
                m={"xs"}
            >
                {error}
            </Alert>
        </ScrollArea>
    );

    if (stage === "filters") {
        if (classifiersLoading) {
            content = getLoader();
        } else {
            if (classifiersError) {
                content = getError(classifiersError);
            } else {
                content = (
                    <PolicyMapFilters
                        classifiers={classifiers}
                        showData={showData}
                    />
                );
            }
        }
    } else if (stage === "view") {
        if (classificationLoading) {
            content = getLoader();
        } else {
            if (classificationError || !classification) {
                content = getError(classificationError ?? "unknown error");
            } else {
                content = (
                    <>
                        <PolicyMapView data={classification} />
                        <Button
                            radius="xl"
                            onClick={(_) => setStage("filters")}
                            style={{
                                position: "absolute",
                                top: "1rem",
                                left: "1rem",
                            }}
                        >
                            Back
                        </Button>
                    </>
                );
            }
        }
    }

    return (
        <div
            style={{
                width: "100vw",
                height: `calc(100vh - ${HEADER_HEIGHT})`,
                position: "relative",
                backgroundColor: isDark ? theme.colors.gray[8] : "#F5F5DC",
                overflow: "hidden",
            }}
        >
            {content}
        </div>
    );
}
