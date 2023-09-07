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
    PasswordInput,
    Select,
    Text,
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
                        <PasswordInput
                            withAsterisk
                            label="Key"
                            placeholder=""
                            {...form.getInputProps("aws_key")}
                        />
                        <PasswordInput
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
                        <PasswordInput
                            withAsterisk
                            label="Subscription ID"
                            placeholder=""
                            {...form.getInputProps("azure_subscription_id")}
                        />
                        <PasswordInput
                            withAsterisk
                            label="Tenant ID"
                            placeholder=""
                            {...form.getInputProps("azure_tenant_id")}
                        />
                        <PasswordInput
                            withAsterisk
                            label="Client ID"
                            placeholder=""
                            {...form.getInputProps("azure_client_id")}
                        />
                        <PasswordInput
                            withAsterisk
                            label="Client Secret"
                            placeholder=""
                            {...form.getInputProps("azure_client_secret")}
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
                                    <PasswordInput
                                        withAsterisk
                                        label="Key"
                                        placeholder=""
                                        {...form.getInputProps("aws_key")}
                                    />
                                    <PasswordInput
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
                {form.values.cloud_type === "AZURE" && (
                    <List type="ordered" w="90%">
                        <List.Item w="100%">
                            How to obtain Subscription ID:
                            <List listStyleType="disc" w="100%">
                                <List.Item>
                                    {" "}
                                    Sign in to the Azure portal{" "}
                                </List.Item>
                                <List.Item>
                                    {" "}
                                    Navigate to <b>Subscriptions</b>{" "}
                                </List.Item>
                                <List.Item>
                                    {" "}
                                    Copy <b>Subscription ID</b> into Oazis
                                    Defender
                                </List.Item>
                            </List>
                        </List.Item>
                        <PasswordInput
                            withAsterisk
                            label="Subscription ID"
                            placeholder=""
                            {...form.getInputProps("azure_subscription_id")}
                        />
                        <br/>
                        <List.Item>
                            Register the application in Azure:
                            <List listStyleType="disc">
                                <List.Item>
                                    Navigate to <b>App registrations</b>
                                </List.Item>
                                <List.Item>
                                    On the <b>App registrations</b> page, select{" "}
                                    <b>+ New registration</b>
                                </List.Item>
                                <List.Item>
                                    On the <b>Register an application</b> page, fill
                                    out the form as follows:
                                    <br />
                                    for <b>Name</b> enter <i>Oasis Defender</i>,
                                    <br />
                                    for <b>
                                        Supported account types
                                    </b> select{" "}
                                    <i>
                                        Accounts in this organizational
                                        directory only
                                    </i>
                                    .
                                </List.Item>
                                <List.Item>
                                    Select Register to register your app and
                                    create the application service principal.
                                </List.Item>
                            </List>
                        </List.Item>
                        <List.Item>
                            On the App registration page for{" "}
                            <b>Oasis Defender</b> app copy{" "}
                            <b>Directory (tenant) ID</b> into:
                        </List.Item>
                        <PasswordInput
                            withAsterisk
                            label="Tenant ID"
                            placeholder=""
                            {...form.getInputProps("azure_tenant_id")}
                        />
                        <br/>
                        <List.Item>
                            On the App registration page for{" "}
                            <b>Oasis Defender</b> app copy{" "}
                            <b>Application (client) ID</b> into:
                        </List.Item>
                        <PasswordInput
                            withAsterisk
                            label="Client ID"
                            placeholder=""
                            {...form.getInputProps("azure_client_id")}
                        />
                        <br/>
                        <List.Item>
                            Add new client secret:
                            <List listStyleType="disc">
                                <List.Item>
                                    On the <b>Certificates & secrets</b> page
                                </List.Item>
                                <List.Item>
                                    Select <b>+ New client secret</b> the{" "}
                                    <b>Add a client secret</b> dialog will pop
                                    out from the right-hand side of the page. In
                                    this dialog:
                                    <br />
                                    for <b>Description</b> enter{" "}
                                    <i>Oasis Defender app</i>,
                                    <br />
                                    for <b>Expires</b> select a value of 24
                                    months.
                                </List.Item>
                                <List.Item>
                                    Select <b>Add</b> to add the secret.
                                </List.Item>
                                <List.Item>
                                    On the <b>Certificates & secrets</b> page,
                                    you will be shown the value of the client
                                    secret. Copy the secret <b>Value</b>, as it
                                    will be shown only once.
                                </List.Item>
                            </List>
                        </List.Item>
                        <PasswordInput
                            withAsterisk
                            label="Client Secret"
                            placeholder=""
                            {...form.getInputProps("azure_client_secret")}
                        />
                        <br/>
                        <List.Item>
                            Assign roles to the application service principal:
                            <List listStyleType="disc">
                                <List.Item>
                                    Navigate to <b>Resource groups</b>
                                </List.Item>
                                <List.Item>
                                    {" "}
                                    On the page for the resource group, which
                                    should be added to Oasis Defender, select{" "}
                                    <b>Access control (IAM)</b> from the
                                    left-hand menu
                                </List.Item>
                                <List.Item>
                                    Select the <b>Role assignments</b> tab{" "}
                                </List.Item>
                                <List.Item>
                                    Select <b>+ Add</b> from the top menu and
                                    then <b>Add role assignment</b> from the
                                    resulting drop-down menu{" "}
                                </List.Item>
                                <List.Item>
                                    To create <b>ReadOnly</b> account: <br />
                                    Select role <b>Reader</b> and press{" "}
                                    <b>Next</b> button.
                                </List.Item>
                                <List.Item>
                                    The Select text box can be used to filter
                                    the list of users and groups inyour
                                    subscription. Type <i>Oasis Defender</i>.
                                </List.Item>
                                <List.Item>
                                    Select the service principal associated with{" "}
                                    <b>Oasis Defender</b> application.
                                </List.Item>
                                <List.Item>
                                    Select <b>Select</b> at the bottom of the
                                    dialog to continue
                                </List.Item>
                                <List.Item>
                                    The service principal will now show as
                                    selected on the <b>Add role assignment</b>{" "}
                                    screen
                                </List.Item>
                                <List.Item>
                                    Select <b>Review + assign</b> to go to the
                                    final page and then <b>Review + assign</b>{" "}
                                    again to complete the process.
                                </List.Item>
                            </List>
                        </List.Item>
                        <br/>
                        <Text>
                            For more information, visit the{" "}
                            <a href="https://learn.microsoft.com/ru-ru/azure/developer/python/sdk/authentication-on-premises-apps?tabs=azure-portal">
                                Azure Help page
                            </a>
                        </Text>
                    </List>
                )}
                <Group position="right" mt="md">
                    <Button color="blue" onClick={closeCloudHelp}>
                        Continue
                    </Button>
                </Group>
            </Modal>
        </>
    );
};
