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

function App() {
    const [colorScheme, setColorScheme] = useState<ColorScheme>("light");
    const toggleColorScheme = (value?: ColorScheme) => {
        setColorScheme(value || (colorScheme === "dark" ? "light" : "dark"));
    };

    useEffect(() => {
        document.body.style.background =
            colorScheme === "dark" ? "#343A40" : "#F5F5DC";
    }, [colorScheme]);

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
            label: "Analyze",
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
                        </Routes>
                    </ModalsProvider>
                </MantineProvider>
            </ColorSchemeProvider>
        </Router>
    );
}

export default App;
