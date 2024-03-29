import React, { useState } from "react";
import { useForm } from "@mantine/form";
import { ICloudCreate } from "../core/models/ICloud";
import {
    Anchor,
    Button,
    Code,
    CopyButton,
    Group,
    List,
    Modal,
    NativeSelect,
    PasswordInput,
    SegmentedControl,
    Select,
    Text,
    TextInput,
    Title,
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
    const [addCloudManualType, setAddCloudManualType] = useState("script"); // "script" | "manual"

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
                            How can I set up an access for Oasis Defender?
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
                            How can I set up an access for Oasis Defender?
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
                title=<Title order={4}>
                    {" "}
                    Connect Your Cloud with Oasis Defender
                </Title>
                opened={cloudHelpOpened}
                onClose={closeCloudHelp}
                zIndex={300}
                size="auto"
                centered
            >
                <SegmentedControl
                    value={addCloudManualType}
                    onChange={setAddCloudManualType}
                    fullWidth
                    data={[
                        { label: "Script", value: "script" },
                        { label: "Manual", value: "manual" },
                    ]}
                    mb="sm"
                />

                {form.values.cloud_type === "AWS" &&
                    addCloudManualType === "script" &&
                    cloudConnectAWSScript()}

                {form.values.cloud_type === "AWS" &&
                    addCloudManualType === "manual" &&
                    cloudConnectAWSManual()}

                {form.values.cloud_type === "AZURE" &&
                    addCloudManualType === "script" &&
                    cloudConnectAzureScript()}

                {form.values.cloud_type === "AZURE" &&
                    addCloudManualType === "manual" &&
                    cloudConnectAzureManual()}

                <Group position="right" mt="md">
                    <Button color="blue" onClick={closeCloudHelp}>
                        Continue
                    </Button>
                </Group>
            </Modal>
        </>
    );

    function cloudConnectAWSScript(): React.ReactNode {
        return (
            <List type="ordered" w="90%">
                <List.Item>
                    Download{" "}
                    <Anchor
                        onClick={(e) => {
                            fetch(
                                "https://raw.githubusercontent.com/OasisDefender/OasisUsersCreation/main/aws/CloudFormation/OasisUserCloudFormationTemplate.json"
                            )
                                .then((response) => response.blob())
                                .then((blob) => {
                                    const link = document.createElement("a");
                                    link.href = URL.createObjectURL(blob);
                                    link.download =
                                        "OasisUserCloudFormationTemplate.json";
                                    link.click();
                                })
                                .catch(console.error);
                        }}
                    >
                        CloudFormation template
                    </Anchor>{" "}
                    from OasisDefender GitHub repository
                </List.Item>
                <List.Item>
                    Apply the downloaded CloudFormation template on AWS
                </List.Item>
                <List.Item>
                    From the created CloudFormation Stack Outputs, insert both{" "}
                    <b>OasisAccessKey</b> and <b>OasisSecretKey</b> into
                    OasisDefender:
                </List.Item>
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
            </List>
        );
    }

    function cloudConnectAWSManual(): React.ReactNode {
        return (
            <List type="ordered" w="90%">
                <List.Item>
                    Creating a New IAM User
                    <List listStyleType="disc">
                        <List.Item>
                            Sign in to your <b>AWS Management Console</b>
                        </List.Item>
                        <List.Item>
                            and go to the{" "}
                            <b>IAM (Identity and Access Management)</b> service
                        </List.Item>
                        <List.Item>
                            Select <b>Users</b> in the left navigation pane
                        </List.Item>
                        <List.Item>
                            Click the <b>Create User</b> button to create a new
                            user
                        </List.Item>
                        <List.Item>
                            Specify a username for the new user
                        </List.Item>
                    </List>
                </List.Item>
                <List.Item>
                    Set User Permissions
                    <List listStyleType="disc">
                        <List.Item>
                            Choose <b>Attach policies directly</b> from the{" "}
                            <b>Permissions options</b>
                        </List.Item>
                        <List.Item>
                            To create a <b>read-only</b> account:
                            <List listStyleType="circle">
                                <List.Item>
                                    Ensure the <b>SecurityAudit</b> policy is
                                    selected
                                </List.Item>
                            </List>
                        </List.Item>
                        <List.Item>
                            Review the user's settings and permissions, then
                            confirm
                        </List.Item>
                    </List>
                </List.Item>
                <List.Item>
                    Create the access key
                    <List listStyleType="disc">
                        <List.Item>
                            Click on the name of the user you created in the
                            list of users
                        </List.Item>
                        <List.Item>
                            Then click on the <b>Create access key</b> button to
                            generate an access key
                        </List.Item>
                        <List.Item>
                            Select the <b>Application running outside AWS</b>{" "}
                            use case
                        </List.Item>
                        <List.Item>Create the Access Key</List.Item>
                        <List.Item>
                            <i>Optional:</i> After creating the access key,
                            obtain a CSV file with the Access Key ID and Secret
                            Access Key
                        </List.Item>
                        <List.Item>
                            Next, insert both the <b>Access key</b> and{" "}
                            <b>Secret access key</b> into Oasis Defender:
                        </List.Item>
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
                    </List>
                </List.Item>
            </List>
        );
    }

    function cloudConnectAzureScript(): React.ReactNode {
        const azureScript =
            "curl -s https://raw.githubusercontent.com/OasisDefender/OasisUsersCreation/main/azure/azure_user.sh | bash";

        return (
            <List type="ordered" w="90%">
                <List.Item>
                    Open Azure CloudShell console in Bash mode
                </List.Item>
                <List.Item>
                    Execute script from OasisDefender GitHub repository:
                </List.Item>
                <CopyButton value={azureScript}>
                    {({ copied, copy }) => (
                        <Button color={copied ? "teal" : "blue"} onClick={copy}>
                            {copied ? "Code copied" : "Copy code"}
                        </Button>
                    )}
                </CopyButton>
                <Code block mt="sm" mb="sm">
                    {azureScript}
                </Code>
                <List.Item>
                    From the script outputs, insert <b>Tenant</b>,{" "}
                    <b>Subscription</b>, <b>App</b> and <b>Secret</b> into
                    OasisDefender:
                </List.Item>
                <PasswordInput
                    withAsterisk
                    label="Tenant ID"
                    placeholder=""
                    {...form.getInputProps("azure_tenant_id")}
                />
                <PasswordInput
                    withAsterisk
                    label="Subscription ID"
                    placeholder=""
                    {...form.getInputProps("azure_subscription_id")}
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
            </List>
        );
    }

    function cloudConnectAzureManual(): React.ReactNode {
        return (
            <List type="ordered" w="90%">
                <List.Item w="100%">
                    Obtain a Subscription ID:
                    <List listStyleType="disc" w="100%">
                        <List.Item> Sign in to the Azure portal </List.Item>
                        <List.Item>
                            {" "}
                            Navigate to <b>Subscriptions</b>{" "}
                        </List.Item>
                        <List.Item>
                            {" "}
                            Insert the <b>Subscription ID</b> into Oazis
                            Defender:
                        </List.Item>
                    </List>
                </List.Item>
                <PasswordInput
                    withAsterisk
                    label="Subscription ID"
                    placeholder=""
                    {...form.getInputProps("azure_subscription_id")}
                />

                <br />
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
                            On the <b>Register an application</b> page, fill out
                            the form as follows:
                            <br />
                            for <b>Name</b> enter <i>Oasis Defender</i>,
                            <br />
                            for <b>Supported account types</b> select{" "}
                            <i>
                                Accounts in this organizational directory only
                            </i>
                            .
                        </List.Item>
                        <List.Item>
                            Select Register to register your application and
                            create the application service principal.
                        </List.Item>
                    </List>
                </List.Item>
                <List.Item>
                    On the App registration page for the application copy the{" "}
                    <b>Directory (tenant) ID</b> to <b>Oasis Defender</b>:
                </List.Item>
                <PasswordInput
                    withAsterisk
                    label="Tenant ID"
                    placeholder=""
                    {...form.getInputProps("azure_tenant_id")}
                />
                <br />
                <List.Item>
                    On the App registration page for the application copy the{" "}
                    <b>Application (client) ID</b> to <b>Oasis Defender</b>:
                </List.Item>
                <PasswordInput
                    withAsterisk
                    label="Client ID"
                    placeholder=""
                    {...form.getInputProps("azure_client_id")}
                />
                <br />
                <List.Item>
                    Add a new client secret:
                    <List listStyleType="disc">
                        <List.Item>
                            On the <b>Certificates & secrets</b> page
                        </List.Item>
                        <List.Item>
                            Select <b>+ New client secret</b> the{" "}
                            <b>Add a client secret</b> dialog will pop out from
                            the right-hand side of the page. In the dialogue:
                            <br />
                            for <b>Description</b> enter{" "}
                            <i>Oasis Defender app</i>,
                            <br />
                            for <b>Expires</b> select <i>24 months</i>.
                        </List.Item>
                        <List.Item>
                            Select <b>Add</b> to add the secret.
                        </List.Item>
                        <List.Item>
                            On the <b>Certificates & secrets</b> page, you will
                            be shown the value of the client secret. It will be
                            shown only once! Insert the secret <b>Value</b> into{" "}
                            <b>Oasis Defender:</b>
                        </List.Item>
                    </List>
                </List.Item>
                <PasswordInput
                    withAsterisk
                    label="Client Secret"
                    placeholder=""
                    {...form.getInputProps("azure_client_secret")}
                />
                <br />
                <List.Item>
                    Assign roles to the application service principal:
                    <List listStyleType="disc">
                        <List.Item>
                            Navigate to <b>Resource groups</b>
                        </List.Item>
                        <List.Item>
                            {" "}
                            On the page for the resource group, which should be
                            added to Oasis Defender, select{" "}
                            <b>Access control (IAM)</b> from the left-hand menu
                        </List.Item>
                        <List.Item>
                            Select the <b>Role assignments</b> tab{" "}
                        </List.Item>
                        <List.Item>
                            Select <b>+ Add</b> from the top menu and then{" "}
                            <b>Add role assignment</b> from the resulting
                            drop-down menu{" "}
                        </List.Item>
                        <List.Item>
                            To create a <b>read-only</b> account: <br />
                            Select role <b>Reader</b> and press <b>Next</b>{" "}
                            button.
                        </List.Item>
                        <List.Item>
                            The Select text box can be used to filter the list
                            of users and groups inyour subscription. Type{" "}
                            <i>Oasis Defender</i>.
                        </List.Item>
                        <List.Item>
                            Select the service principal associated with{" "}
                            <b>Oasis Defender</b> application.
                        </List.Item>
                        <List.Item>
                            Select <b>Select</b> at the bottom of the dialog to
                            continue
                        </List.Item>
                        <List.Item>
                            The service principal will now show as selected on
                            the <b>Add role assignment</b> screen
                        </List.Item>
                        <List.Item>
                            Select <b>Review + assign</b> to go to the final
                            page and then <b>Review + assign</b> again to
                            complete the process.
                        </List.Item>
                    </List>
                </List.Item>
                <br />
                <Text>
                    For more information, visit the{" "}
                    <a href="https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication-on-premises-apps?tabs=azure-portal">
                        Azure Help page
                    </a>
                </Text>
            </List>
        );
    }
};
