import { NavigateFunction } from "react-router-dom";


export type SetGlobalMessageCallbackFunc = (button: string, navigate: NavigateFunction) => void;
export type SetGlobalMessageFunc = (title: string, message: string, buttons: string[], callback: SetGlobalMessageCallbackFunc) => boolean;

declare global {
    var setGlobalMessage: SetGlobalMessageFunc | undefined;
}

global.setGlobalMessage = undefined;
export { };

