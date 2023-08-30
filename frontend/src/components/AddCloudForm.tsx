import React from "react";
import { useForm } from "@mantine/form";
import { ICloudCreate } from "../core/models/ICloud";
import {
    Anchor,
    Button,
    Group,
    List,
    Modal,
    NativeSelect,
    Select,
    TextInput,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

interface AddCloudFormProps {
    onCancel: () => void;
    makeAddCloud: (cloud: ICloudCreate) => void;
}

export const AddCloudForm = ({ onCancel, makeAddCloud }: AddCloudFormProps) => {
    const [cloudHelpOpened, { open: openCloudHelp, close: closeCloudHelp }] =
        useDisclosure(false);
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
                        <Anchor
                            component="button"
                            type="button"
                            w="100%"
                            pt="xs"
                            onClick={openCloudHelp}
                        >
                            How to create an Access Key for Oasis Defender?
                        </Anchor>
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
                        <Anchor
                            component="button"
                            type="button"
                            w="100%"
                            pt="xs"
                            onClick={openCloudHelp}
                        >
                            How to create an access for Oasis Defender?
                        </Anchor>
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
            <Modal
                title="How to Connect Your Cloud with Oasis Defender"
                opened={cloudHelpOpened}
                onClose={closeCloudHelp}
                zIndex={300}
                size="auto"
                centered
            >
                {form.values.cloud_type === "AWS" && (
                    <List type="ordered" w="90%">
                        <List.Item>
                            Create a New IAM User
                            <List listStyleType="disc">
                                <List.Item>
                                    Log in to your AWS Management Console
                                </List.Item>
                                <List.Item>
                                    Navigate to the IAM (Identity and Access
                                    Management) service
                                </List.Item>
                                <List.Item>
                                    Click on "Users" in the left navigation pane
                                </List.Item>
                                <List.Item>
                                    Click the "Create user" button to create a
                                    new user
                                </List.Item>
                                <List.Item>
                                    Provide a username for the new user
                                </List.Item>
                            </List>
                        </List.Item>
                        <List.Item>
                            Set User Permissions
                            <List listStyleType="disc">
                                <List.Item>
                                    Select "Attach policies directly" in the
                                    "Permissions options"
                                </List.Item>
                                <List.Item>
                                    To create <b>ReadOnly</b> account:
                                    <List listStyleType="circle">
                                        <List.Item>
                                            Check policy with the name
                                            "SecurityAudit"
                                        </List.Item>
                                    </List>
                                </List.Item>
                                <List.Item>
                                    Review your user's settings and permissions,
                                    and confirm
                                </List.Item>
                            </List>
                        </List.Item>
                        <List.Item>
                            Create Access Key
                            <List listStyleType="disc">
                                <List.Item>
                                    Click on the name of created user in Users
                                    list
                                </List.Item>
                                <List.Item>
                                    Click on the "Create access key" button to
                                    generate an Access Key
                                </List.Item>
                                <List.Item>
                                    Choose the "Application running outside AWS"
                                    use case
                                </List.Item>
                                <List.Item>Create the Access Key</List.Item>
                                <List.Item>
                                    After creating the access key, you'll be
                                    able to download a CSV file containing the
                                    Access Key ID and Secret Access Key
                                </List.Item>
                                <List.Item>
                                    Copy the "Access key" and "Secret access
                                    key" into Oasis Defender
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
                                        {...form.getInputProps(
                                            "aws_secret_key"
                                        )}
                                    />
                                </List.Item>
                            </List>
                        </List.Item>
                    </List>
                )}
            </Modal>
        </>
    );
};
