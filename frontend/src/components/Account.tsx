import { Button, Container, Title, Text, Anchor } from "@mantine/core";

import { Auth } from "aws-amplify";
import { basicLogout } from "../core/basic";

interface AccountProps {    
}

export function Account({ }: AccountProps) {
    let logout : (() => void) | undefined = undefined;

    if (global.config.authType === "BASIC") {
        logout = () => {
            basicLogout();
        };
    }
    else if (global.config.authType === "COGNITO") {
        logout = () => {
            Auth.signOut();
        };
    }

    return (
        <Container p="md">
          {logout && <Button onClick={logout} style={{ float: 'right' }}>Logout</Button>}
          <Title>Oasis Defender</Title>
          <Text>
            Visit our website: <Anchor href="https://oasisdefender.com" target="_blank">oasisdefender.com</Anchor>
          </Text>
          <Text>
            Check out our Github: <Anchor href="https://github.com/OasisDefender/oasis" target="_blank">github.com/OasisDefender/oasis</Anchor>
          </Text>
        </Container>
    );
}