import React, {
    useEffect,
    useRef,
    useState,
} from "react";

import { HEADER_HEIGHT } from "../components/Header";
import {
    Alert,
    Button,
    Loader,
    ScrollArea,
    useMantineTheme,
} from "@mantine/core";
import PolicyMapFilters, {
    IClassifierExt,
} from "../components/PolicyMapFilters";
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

    const [classifiersExt, setClassifiersExt] = useState<IClassifierExt[]>([]);
    useEffect(() => {
        if (classifiers) {
            const newValue = classifiers.map((classifier) => ({
                ...classifier,
                isChecked: false,
            }));
            setClassifiersExt(newValue);
        } else {
            setClassifiersExt([]);
        }
    }, [classifiers]);

    const {
        loading: classificationLoading,
        error: classificationError,
        data: classification,
        fetchData: fetchClassification,
        toogleChildren
    } = usePolicyMap();

    const selectedRef = useRef(selected);

    useEffect(() => {
        selectedRef.current = selected;
    }, [selected]);

    const toogleClassifiers = (id: number) => {
        setClassifiersExt((oldValue) =>
            oldValue.map((item) => {
                if (item.id === id) {
                    return {
                        ...item,
                        isChecked: !item.isChecked,
                    };
                }
                return item;
            })
        );
    };

    const reorderClassifiers = (from: number, to: number) => {
        setClassifiersExt((oldValue) => {
            const updatedClassifiers = [...oldValue];
            const [movedItem] = updatedClassifiers.splice(from, 1);
            updatedClassifiers.splice(to, 0, movedItem);
            return updatedClassifiers;
        });
    };

    const showData = () => {
        fetchClassification(
            classifiersExt
                .filter((item) => item.isChecked)
                .map((item) => item.id)
        );
        setStage("view");
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
                        classifiers={classifiersExt}
                        toogle={toogleClassifiers}
                        reorder={reorderClassifiers}
                        next={showData}
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
                        <PolicyMapView data={classification.scheme} lines={classification.lines} toogleChildren={toogleChildren} />
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
