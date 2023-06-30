import React from "react";
import { useForm } from "@mantine/form";
import { Button, Group, TextInput } from "@mantine/core";

interface AddTargetFormProps {
    onCancel: () => void;
    makeAddTarget: ({ target }: { target: string }) => void;
}

export const AddTargetForm = ({
    onCancel,
    makeAddTarget,
}: AddTargetFormProps) => {
    const form = useForm({
        initialValues: {
            target: "",
        },

        validate: {
            target: (value) =>
                /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\/(3[0-2]|[1-2]?\d)$/.test(
                    value
                )
                    ? null
                    : 'Invalid network. Ex: "192.168.1.0/24" or "8.8.8.8/32"',
        },
    });

    return (
        <>
            <form onSubmit={form.onSubmit(makeAddTarget)}>
                <TextInput
                    withAsterisk
                    label="Network"
                    placeholder="xxx.xxx.xxx.xxx/xx"
                    data-autofocus
                    {...form.getInputProps("target")}
                />

                <Group position="right" mt="md">
                    <Button onClick={onCancel} variant="default">
                        Cancel
                    </Button>
                    <Button color="blue" type="submit">
                        Add target
                    </Button>
                </Group>
            </form>
        </>
    );
};
