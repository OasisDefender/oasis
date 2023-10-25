import React, {
    useEffect,
    useRef,
    useState,
} from "react";

import { HEADER_HEIGHT } from "../components/Header";
import {
    Alert,
    Loader,
    ScrollArea,
} from "@mantine/core";
import { IconAlertTriangle } from "@tabler/icons-react";
import { useAnalyzeView } from "../core/hooks/analyzeview";
import AnalyzeViewView from "../components/AnalyzeViewView";
import { useParams } from 'react-router';

export function AnalyzeView() {
    const viewName = useParams<{ viewName: string }>().viewName;

    const {
        loading,
        error,
        data,
        fetchData,
        toogleChildren
    } = useAnalyzeView({ name: viewName ?? "" });    

    useEffect(() => {
        fetchData();
    }, [viewName]);

    const [selected, setSelected] = useState<string | undefined>(undefined);    
    const selectedRef = useRef(selected);
    useEffect(() => {
        selectedRef.current = selected;
    }, [selected]);

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
                title="Cannot get data"
                color="red"
                m={"xs"}
            >
                {error}
            </Alert>
        </ScrollArea>
    );


    if (loading) {
        content = getLoader();
    } else {
        if (error || !data) {
            content = getError(error ?? "unknown error");
        } else {
            content = (<AnalyzeViewView data={data.scheme} lines={data.lines} toogleChildren={toogleChildren} />);
        }
    }


    return (
        <div
            style={{
                width: "100vw",
                height: `calc(100vh - ${HEADER_HEIGHT})`,
                position: "relative",
                overflow: "hidden",
            }}
        >
            {content}
        </div>
    );
}
