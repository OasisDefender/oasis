import {} from "./config"

import ReactDOM from "react-dom/client";
import CognitoApp from "./CognitoApp";
import App from "./App";
import { basicLogout } from "./core/basic";

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

if (global.config.authType === "COGNITO") {    
    root.render(<CognitoApp/>);
}
else {
    if (global.config.authType === "BASIC") {    
        root.render(<App logout={basicLogout}/>);
    }
    else {
        root.render(<App/>);
    }
}
