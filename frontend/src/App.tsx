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

function App() {
    const [colorScheme, setColorScheme] = useState<ColorScheme>("light");
    const toggleColorScheme = (value?: ColorScheme) => {
        setColorScheme(value || (colorScheme === "dark" ? "light" : "dark"));
    };
    const { fetch, maxSeverity } = useHeaderInfo();

    useEffect(() => {
        document.body.style.background =
            colorScheme === "dark" ? "#343A40" : "#F5F5DC";
    }, [colorScheme]);

    const { start } = useInterval(fetch, 60000);
    useEffect(() => {
        start();
    }, []);

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
            link: "/analyze",
            label: (
                <>
                    {maxSeverity && (
                        <IconCircle
                            size="12px"
                            stroke="0.05rem"
                            fill={severityToColor(maxSeverity)}
                        />
                    )}
                    {" Security Analysis"}
                </>
            ),
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
                        <Header links={headerLinks} />
                        <Routes>
                            <Route path="/clouds" element={<Clouds />} />
                            <Route path="/map" element={<CloudMap />} />
                            <Route path="/storages" element={<StoragesMap />} />
                            <Route path="/policy" element={<PolicyMap />} />
                            <Route path="/analyze" element={<Analyze />} />
                            <Route
                                path="/"
                                element={<Navigate replace to="/clouds" />}
                            />
                            <Route path="/logout" element={<Logout />} />
                        </Routes>
                    </ModalsProvider>
                </MantineProvider>
            </ColorSchemeProvider>
        </Router>
    );
}

function Logout() {
    window.location.href = '/';
    return null;
  }

export default App;
