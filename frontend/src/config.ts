export type CognitoSettings = {
    region: string;
    userPoolId: string;
    userPoolWebClientId: string;
};

export type ODConfig = {
    version?: string;
    GMTId?: string;
    backendURI?: string;
    authType?: "COGNITO" | "BASIC";
    cognitoSettings?: CognitoSettings;
};


console.log("Starting config creating...");

let authType = process.env.REACT_APP_AUTH_TYPE?.toUpperCase();
if (authType && (authType !== "COGNITO") && (authType !== "BASIC")) {    
    throw new Error(`Unknown env.REACT_APP_AUTH_TYPE "${authType}"!`);
}


var cognitoSettings: CognitoSettings | undefined;
if (authType === "COGNITO") {
    if (!process.env.REACT_APP_COGNITO_REGION) {
        throw new Error(`Missing env.REACT_APP_COGNITO_REGION`);
    }
    if (!process.env.REACT_APP_COGNITO_USERPOOLID) {
        throw new Error(`Missing env.REACT_APP_COGNITO_USERPOOLID`);
    }
    if (!process.env.REACT_APP_COGNITO_USERPOOLWEBCLIENTID) {
        throw new Error(`Missing env.REACT_APP_COGNITO_USERPOOLWEBCLIENTID`);
    }
    
    cognitoSettings = {
        region: process.env.REACT_APP_COGNITO_REGION,
        userPoolId: process.env.REACT_APP_COGNITO_USERPOOLID,
        userPoolWebClientId: process.env.REACT_APP_COGNITO_USERPOOLWEBCLIENTID
    };
}

let odConfig: ODConfig = {
    version: process.env.REACT_APP_VERSION,
    GMTId: process.env.REACT_APP_GTM_ID,
    backendURI: process.env.REACT_APP_BACKEND_URI,
    authType: authType as ("COGNITO" | "BASIC" | undefined),
    cognitoSettings: cognitoSettings,
};

declare global {
    var config : ODConfig;
}
global.config = odConfig;

console.log("Config created:", global.config);

export { };
