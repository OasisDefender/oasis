import {} from "./config";

import ReactDOM from "react-dom/client";
import CognitoApp from "./CognitoApp";
import App from "./App";


const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

if (global.config.authType === "COGNITO") {
    root.render(<CognitoApp />);
} else {
    root.render(<App />);
}
