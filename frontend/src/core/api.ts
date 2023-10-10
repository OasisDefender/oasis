import { Auth } from "aws-amplify";
import axios from "axios";

const api = axios.create({
    baseURL: global.config.backendURI,
});

if (global.config.authType === "COGNITO") {
    api.interceptors.request.use(async (req) => {
        try {
            const session = await Auth.currentSession();
            const jwtToken = session.getIdToken().getJwtToken();

            req.headers.Authorization = jwtToken;
        } catch (error) {
            console.error("Failed to get the Cognito token:", error);
        }

        return req;
    });
}

export { api };
