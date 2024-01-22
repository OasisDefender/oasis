import {} from "./config";

import ReactDOM from "react-dom/client";
import CognitoApp from "./CognitoApp";
import App from "./App";
import InitSettingsProvider from "./core/initsettings/InitSettingsProvider";

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

const app = global.config.authType === "COGNITO" ? <CognitoApp /> : <App />;

root.render(<InitSettingsProvider>{app}</InitSettingsProvider>);
