import React, { useState } from "react";

import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";
import { ColorScheme, ColorSchemeProvider, MantineProvider } from "@mantine/core";

import { HeaderResponsive as Header } from "./components/Header";

import { Clouds } from "./pages/Clouds";
import { CloudMap } from "./pages/CloudMap";
import { ModalsProvider } from "@mantine/modals";

function App() {
    const [colorScheme, setColorScheme] = useState<ColorScheme>('light');
    const toggleColorScheme = (value?: ColorScheme) =>
      setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));
      
    const headerLinks = [
        {
            link: "/clouds",
            label: "My Clouds",
        },
        {
            link: "/map",
            label: "Cloud Map",
        },
    ];

    return (
        <Router>
          <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
            <MantineProvider theme={{ colorScheme }} withGlobalStyles withNormalizeCSS>
                <ModalsProvider>
                    <Header links={headerLinks} />
                    <Routes>
                        <Route path="/clouds" element={<Clouds />} />
                        <Route path="/map" element={<CloudMap />} />
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
