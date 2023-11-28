
import { Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { AxiosError } from "axios";

let zIndex : number = 1000;

export function OasisDecodeError(error : AxiosError) : string {
    if (!error) {
        return "Unknown error";
    }

    console.log(error);
    if (error.response && error.response.status === 500 && error.response.data as string) {
        return error.response.data as string;
    }
    return error.message;
}

export function ShowModalErrorMessage(title: string, message: string) {
    modals.open({
        title: title,
        centered: true,
        onClose: () => {
            zIndex -= 10;
        },
        zIndex: zIndex,
        children: (
            <Text mt={"xs"}>
                    {message}
            </Text>
        )        
    });
    zIndex += 10;
}

export function ShowModalError(title: string, error: AxiosError) {
    const message = OasisDecodeError(error);
    ShowModalErrorMessage(title, message);
}