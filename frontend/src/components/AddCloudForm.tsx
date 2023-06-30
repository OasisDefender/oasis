import React from "react";
import { useForm } from "@mantine/form";
import { ICloudCreate } from "../core/models/ICloud";
import { Button, Group, NativeSelect, Select, TextInput } from "@mantine/core";

interface AddCloudFormProps {
    onCancel: () => void;
    makeAddCloud: (cloud: ICloudCreate) => void;
}

export const AddCloudForm = ({ onCancel, makeAddCloud }: AddCloudFormProps) => {
    const cloudTypes = ["AWS", "AZURE"];
    const awsRegions = [
        "ap-east-1",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-northeast-3",
        "ap-south-1",
        "ap-south-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-southeast-3",
        "ap-southeast-4",
        "ca-central-1",
        "eu-central-1",
        "eu-central-2",
        "eu-north-1",
        "eu-south-1",
        "eu-south-2",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "me-central-1",
        "me-south-1",
        "sa-east-1",
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
    ];

    const form = useForm<ICloudCreate>({
        initialValues: {
            name: "",
            cloud_type: "AWS",

            aws_region: "",
            aws_key: "",
            aws_secret_key: "",

            azure_subscription_id: "",
            azure_tenant_id: "",
            azure_client_id: "",
            azure_client_secret: "",
        },

        validate: {
            name: (value) =>
                value.length < 2 ? "Name must have at least 2 letters" : null,
            cloud_type: (value) =>
                cloudTypes.indexOf(value) >= 0 ? null : "Invalid value",

            aws_region: (value, values) =>
                values.cloud_type !== "AWS" || awsRegions.indexOf(value) >= 0
                    ? null
                    : "Invalid value",
            aws_key: (value, values) =>
                values.cloud_type !== "AWS" || value.length >= 2
                    ? null
                    : "Invalid value",
            aws_secret_key: (value, values) =>
                values.cloud_type !== "AWS" || value.length >= 2
                    ? null
                    : "Invalid value",

            azure_subscription_id: (value, values) =>
                values.cloud_type !== "AZURE" || value.length >= 2
                    ? null
                    : "Invalid value",
            azure_tenant_id: (value, values) =>
                values.cloud_type !== "AZURE" || value.length >= 2
                    ? null
                    : "Invalid value",
            azure_client_id: (value, values) =>
                values.cloud_type !== "AZURE" || value.length >= 2
                    ? null
                    : "Invalid value",
            azure_client_secret: (value, values) =>
                values.cloud_type !== "AZURE" || value.length >= 2
                    ? null
                    : "Invalid value",
        },
    });

    return (
        <>
            <form onSubmit={form.onSubmit(makeAddCloud)}>
                <TextInput
                    withAsterisk
                    label="Name"
                    placeholder="Cloud name"
                    data-autofocus
                    {...form.getInputProps("name")}
                />

                <NativeSelect
                    data={cloudTypes}
                    label="Select cloud type"
                    withAsterisk
                    {...form.getInputProps("cloud_type")}
                />

                {form.values.cloud_type === "AWS" && (
                    <>
                        <Select
                            label="Region"
                            placeholder="Pick one"
                            searchable
                            nothingFound="No regions"
                            data={awsRegions}
                            withinPortal={true}
                            withAsterisk
                            {...form.getInputProps("aws_region")}
                        />
                        <TextInput
                            withAsterisk
                            label="Key"
                            placeholder=""
                            {...form.getInputProps("aws_key")}
                        />
                        <TextInput
                            withAsterisk
                            label="Secret Key"
                            placeholder=""
                            {...form.getInputProps("aws_secret_key")}
                        />
                    </>
                )}

                {form.values.cloud_type === "AZURE" && (
                    <>
                        <TextInput
                            withAsterisk
                            label="Subscription ID"
                            placeholder=""
                            {...form.getInputProps("azure_subscription_id")}
                        />
                        <TextInput
                            withAsterisk
                            label="Tenant ID"
                            placeholder=""
                            {...form.getInputProps("azure_tenant_id")}
                        />
                        <TextInput
                            withAsterisk
                            label="Client ID"
                            placeholder=""
                            {...form.getInputProps("azure_client_id")}
                        />
                        <TextInput
                            withAsterisk
                            label="Client Secret"
                            placeholder=""
                            {...form.getInputProps("azure_client_key")}
                        />
                    </>
                )}

                <Group position="right" mt="md">
                    <Button onClick={onCancel} variant="default">
                        Cancel
                    </Button>
                    <Button color="blue" type="submit">
                        Add cloud
                    </Button>
                </Group>
            </form>
        </>
    );
};
