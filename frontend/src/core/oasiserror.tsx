
import { Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { AxiosError } from "axios";

let zIndex : number = 1000;

export function OasisDecodeError(error: AxiosError): string {
    if (!error) {
        return "Unknown error";
    }

    if (error.response && [401, 500].includes(error.response.status)) {
        const responseData = error.response.data;

        if (typeof responseData === "string") {
            return responseData;
        }

        if (typeof responseData === "object" && responseData !== null && "message" in responseData) {
            const message = responseData["message"];
            if (typeof message === "string") {
                return message;
            }
        }
    }

    return error.message;
}


export function ShowModalError(title: string, error: unknown) {
    let msg = "Unknown error";
    if (typeof error === "string") {
        msg = error;
    }
    else if (error instanceof AxiosError) {
        msg = OasisDecodeError(error);
    }
    else if (error instanceof Error) {
        msg = error.message;
    }
    modals.open({
        title: title,
        centered: true,
        onClose: () => {
            zIndex -= 10;
        },
        zIndex: zIndex,
        children: (
            <Text mt={"xs"}>
                    {msg}
            </Text>
        )        
    });
    zIndex += 10;
}