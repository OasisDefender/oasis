import {
    Accordion,
    Alert,
    Badge,
    Container,
    Group,    
    Loader,    
    Space,    
    Table,    
} from "@mantine/core";
import { useAnalyzation } from "../core/hooks/analyzation";
import { IconAlertTriangle } from "@tabler/icons-react";

function jsxJoinLines (array: any[]) {
    return array.length > 0
      ? array.reduce((result, item) => <>{result}<br/>{item}</>)
      : null;
}

export function Analyze() {
    const { loading, error, data } = useAnalyzation();

    return (
        <Container size="xl">
            <Space h="sm" />
            {loading && (
                <Loader
                    sx={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                />
            )}
            {!loading && error && (
                <Alert
                    icon={<IconAlertTriangle size="1rem" />}
                    title="Cannot get analisis results"
                    color="red"
                    mt={"xs"}
                    sx={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: "translate(-50%, -50%)",
                    }}
                >
                    {error}
                </Alert>
            )}
            {!loading && data && (
                <Accordion variant="separated">
                    {data.map((d, i) => (
                        <Accordion.Item value={i.toString()} key={i}>
                            <Accordion.Control>
                                <Group position="apart" spacing="xs">
                                    <b>{d.label}</b>
                                    <Badge size="lg" variant="filled">
                                        {d.data.length}
                                    </Badge>
                                </Group>
                            </Accordion.Control>
                            <Accordion.Panel>
                                <Table striped>
                                    <thead>
                                        <tr>
                                            {d.caption.map((caption, i) => (
                                                <th key={i}>{caption}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {d.data.map((r, j) => (
                                            <tr key={j}>
                                                {r.map((col, i) => (
                                                    <td key={i}>                                                        
                                                        {typeof col === "string" ? col : jsxJoinLines(col)}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </Table>
                            </Accordion.Panel>
                        </Accordion.Item>
                    ))}
                </Accordion>
            )}
        </Container>
    );
}
