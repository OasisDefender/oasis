import { Amplify } from "aws-amplify";

import {
    Authenticator,
    CheckboxField,
    useAuthenticator,
} from "@aws-amplify/ui-react";
import { Flex, Text } from "@mantine/core";

import "@aws-amplify/ui-react/styles.css";
import "./styles/cognitoStyles.css";

import App from "./App";
import { Icon } from "./components/Icon";
import { useEffect } from "react";
import TagManager from "react-gtm-module";

function CognitoApp() {
    Amplify.configure({
        Auth: global.config.cognitoSettings,
    });

    useEffect(() => {
        if (global.config.GMTId) {
            console.log("GTM_ID", global.config.GMTId);

            const tagManagerArgs = {
                gtmId: global.config.GMTId,
            };

            TagManager.initialize(tagManagerArgs);
        }
    }, []);

    const components = {
        Header: () => (
            <Flex justify="center" p="md">
                <Icon size="64" iconTextClasses="cognitoText" />
            </Flex>
        ),
        Footer: () => (
            <Flex justify="center" p="md">
                <Text>&copy; All Rights Reserved</Text>
            </Flex>
        ),
        SignUp: {
            FormFields() {
                const { validationErrors } = useAuthenticator();

                return (
                    <>
                        <Authenticator.SignUp.FormFields />
                        <CheckboxField
                            errorMessage={
                                validationErrors.acknowledgement as string
                            }
                            hasError={!!validationErrors.acknowledgement}
                            name="acknowledgement"
                            value="yes"
                            label={
                                <>
                                    I agree with the{" "}
                                    <a
                                        href="/static/terms.html"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        Terms of Service
                                    </a>
                                </>
                            }
                        />
                    </>
                );
            },
        },
    };

    return (
        <Authenticator
            loginMechanisms={["email"]}
            variation="modal"
            components={components}
            services={{
                async validateCustomSignUp(formData) {
                    if (!formData.acknowledgement) {
                        return {
                            acknowledgement:
                                "You must agree to the Terms of Service",
                        };
                    }
                },
            }}
        >
            {({ signOut, user }) => {
                console.log("signOut", signOut);
                console.log("user", user);
                return <App username={user?.attributes?.email} />;
            }}
        </Authenticator>
    );
}

export default CognitoApp;
