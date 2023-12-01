import { useEffect, useRef, useState } from "react";
import {
    SetGlobalMessageCallbackFunc,
    SetGlobalMessageFunc,
} from "../globalmessage";
import { useNavigate } from "react-router-dom";
import { Button, Group, Modal } from "@mantine/core";

export function GlobalMessage() {
    const navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [title, setTitle] = useState("");
    const [message, setMessage] = useState("");
    const [buttons, setButtons] = useState<string[]>([]);
    const callbackRef = useRef<SetGlobalMessageCallbackFunc | undefined>(undefined);

    useEffect(() => {
        const setGlobalMessage: SetGlobalMessageFunc = (
            new_title,
            new_message,
            new_buttons,
            new_callback
        ) => {
            if (isModalOpen) return false;

            callbackRef.current = new_callback;
            setTitle(new_title);
            setMessage(new_message);
            setButtons(new_buttons);            
            setIsModalOpen(true);

            return true;
        };

        global.setGlobalMessage = setGlobalMessage;

        return () => {
            global.setGlobalMessage = undefined;
        };
    }, [isModalOpen]);

    return (
        <Modal
            opened={isModalOpen}
            title={title}
            centered
            onClose={() => setIsModalOpen(false)}
        >
            {message}
            <Group position="right" mt="md">
                {buttons.map((button, index) => (
                    <Button
                        key={index}
                        color="blue"
                        onClick={() => {
                            if (callbackRef.current) {
                                callbackRef.current(button, navigate);
                            }
                            setIsModalOpen(false);
                        }}
                    >
                        {button}
                    </Button>
                ))}
            </Group>
        </Modal>
    );
}
