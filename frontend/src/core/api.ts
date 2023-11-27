import { Auth } from "aws-amplify";
import axios, {
    AxiosError,
    AxiosInstance,
    AxiosRequestConfig,
    AxiosResponse,
} from "axios";

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
        req.headers.Domain = window.location.hostname;

        return req;
    });

    api.interceptors.response.use(
        function (response) {
            console.log(response);
            return response;
        },
        function (error: AxiosError) {
            if (error.response?.status === 401) {
                let data = error.response?.data as object;
                if (
                    data &&
                    "message" in data &&
                    data["message"] === "Subscription has expired" &&
                    "url" in data &&
                    (data["url"] as string)
                ) {
                    console.log("window.location.href", data["url"] as string);
                    window.location.href = data["url"] as string;
                }
            }
            return Promise.reject(error);
        }
    );
}

export { api };
