import React, { useEffect, useState } from "react";

import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";
import {
    ColorScheme,
    ColorSchemeProvider,
    MantineProvider,
} from "@mantine/core";

import TagManager from "react-gtm-module";

import { HeaderResponsive as Header } from "./components/Header";

import { Clouds } from "./pages/Clouds";
import { CloudMap } from "./pages/CloudMap";
import { ModalsProvider } from "@mantine/modals";
import { PolicyMap } from "./pages/PolicyMap";
import { StoragesMap } from "./pages/StoragesMap";
import { Analyze } from "./pages/Analyze";
import { severityToColor } from "./core/severity";
import { IconCircle } from "@tabler/icons-react";
import { useHeaderInfo } from "./core/hooks/headerInfo";
import { useInterval } from "@mantine/hooks";
import { AnalyzeView } from "./pages/AnalyzeView";
import { Account } from "./components/Account";
import { GlobalMessage } from "./components/GlobalMessage";

interface AppProps {
    username?: string;
}

function App({ username }: AppProps) {
    const [colorScheme, setColorScheme] = useState<ColorScheme>("light");
    const toggleColorScheme = (value?: ColorScheme) => {
        setColorScheme(value || (colorScheme === "dark" ? "light" : "dark"));
    };
    const { fetch, maxSeverity } = useHeaderInfo();
    const headerInfoUpdate = useInterval(fetch, 60000);

    useEffect(() => {
        console.log("App started");

        const defaultStyle = document.body.style.background;
        return () => {
            document.body.style.background = defaultStyle;
        };
    }, []);
    useEffect(() => {
        document.body.style.background =
            colorScheme === "dark" ? "#343A40" : "#F5F5DC";
    }, [colorScheme]);

    useEffect(() => {
        if (global.config.GMTId) {
            console.log("GTM_ID", global.config.GMTId);

            const tagManagerArgs = {
                gtmId: global.config.GMTId,
                dataLayer: {
                    userId: username
                }            
            };

            TagManager.initialize(tagManagerArgs);
        }
    }, []);

    useEffect(() => {
        headerInfoUpdate.start();
        return () => {
            headerInfoUpdate.stop();
        };
    }, [headerInfoUpdate]);

    const headerLinks = [
        {
            link: "/clouds",
            label: "My Clouds",
        },
        {
            link: "/map",
            label: "Cloud Map",
        },
        {
            link: "/storages",
            label: "Storages",
        },
        {
            link: "/policy",
            label: "Policy Map",
        },
        {
            link: "",
            label: (
                <>
                    {maxSeverity !== undefined && (
                        <IconCircle
                            size="12px"
                            stroke="0.05rem"
                            fill={severityToColor(maxSeverity)}
                        />
                    )}
                    {" Security Analysis"}
                </>
            ),
            children: [
                { link: "/analyze", label: "Findings" },
                {
                    link: "/analyze-view/resultsvisualisation1",
                    label: "Security group Issues",
                },
                {
                    link: "/analyze-view/resultsvisualisation2",
                    label: "Subnet NACL Issues",
                },
            ],
        },
    ];

    return (
        <Router>
            <ColorSchemeProvider
                colorScheme={colorScheme}
                toggleColorScheme={toggleColorScheme}
            >
                <MantineProvider
                    theme={{ colorScheme }}
                    withGlobalStyles
                    withNormalizeCSS
                >
                    <ModalsProvider>
                        <Header links={headerLinks} username={username} />
                        <Routes>
                            <Route path="/clouds" element={<Clouds />} />
                            <Route path="/map" element={<CloudMap />} />
                            <Route path="/storages" element={<StoragesMap />} />
                            <Route path="/policy" element={<PolicyMap />} />
                            <Route path="/analyze" element={<Analyze />} />
                            <Route
                                path="/analyze-view/:viewName"
                                element={<AnalyzeView />}
                            />
                            <Route path="/account" element={<Account />} />
                            <Route
                                path="/"
                                element={<Navigate replace to="/clouds" />}
                            />
                        </Routes>
                        <GlobalMessage />
                    </ModalsProvider>
                </MantineProvider>
            </ColorSchemeProvider>
        </Router>
    );
}

export default App;
