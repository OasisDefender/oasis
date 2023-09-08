import axios from "axios";

const api = axios.create({
//	baseURL: backendURI,
});

api.interceptors.request.use((req) => {
	return {
		...req,
//		baseURL: backendURI,
	};
});

export { api };