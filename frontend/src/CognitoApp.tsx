import { Amplify } from "aws-amplify";

import { Authenticator } from "@aws-amplify/ui-react";
import { Flex, Text } from "@mantine/core"

import "@aws-amplify/ui-react/styles.css";
import "./styles/cognitoStyles.css";

import App from "./App";
import { Icon } from "./components/Icon";

function CognitoApp() {
    Amplify.configure({
        Auth: global.config.cognitoSettings,
    });

    const components = {
        Header: () => (
            <Flex justify="center" p="md">
                <Icon size="64" iconTextClasses="cognitoText"/>
            </Flex>
        ),
        Footer: () => (
            <Flex justify="center" p="md">
                <Text>&copy; All Rights Reserved</Text>
            </Flex>
        ),
    };

    return (
        <Authenticator
            loginMechanisms={["email"]}
            variation="modal"
            components={components}
        >
            {({ signOut, user }) => {
                console.log("signOut", signOut);
                console.log("user", user);
                return <App logout={signOut} />;
            }}
        </Authenticator>
    );
}

export default CognitoApp;
