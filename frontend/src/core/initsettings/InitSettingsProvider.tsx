import React, { ReactNode } from "react";
import { useInitSettings } from "../hooks/initsettings";
import { Button, Container, Loader, Text, Title } from "@mantine/core";
import InitSettingsContext from "./InitSettingsContext";

interface InitSettingsProviderProps {
    children: ReactNode;
}

const InitSettingsProvider = ({ children }: InitSettingsProviderProps) => {
    const { loading, error, data } = useInitSettings();

    if (loading) {
        return (
            <Loader
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                }}
            />
        );
    }

    if (error || !data) {
        const refreshPage = () => {
            window.location.reload();
        };

        return (
            <Container
                style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100vh",
                }}
            >
                <Title color="red">Oasis Defender failed to initialize.</Title>
                <Text size="lg" style={{ margin: "20px 0" }}>
                    {error}
                </Text>
                <Button onClick={refreshPage}>Refresh</Button>
            </Container>
        );
    }

    return (
        <InitSettingsContext.Provider value={data}>
            {children}
        </InitSettingsContext.Provider>
    );
};

export default InitSettingsProvider;
