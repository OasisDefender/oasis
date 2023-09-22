import {
    Accordion,
    Alert,
    Badge,
    Container,
    Group,    
    Loader,    
    Space,    
    Table,
    Tooltip,    
} from "@mantine/core";
import { useAnalyzation } from "../core/hooks/analyzation";
import { IconAlertTriangle, IconCircle, IconCircle0Filled, IconCircleDot, IconCircleFilled, IconHammer, IconHelp, IconHelpCircle, IconHelpHexagon, IconHelpOff, IconHelpSmall, IconSettings } from "@tabler/icons-react";
import { severityToColor } from "../core/severity";

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
                                    <Group>                                        
                                        <Tooltip label={`Severity: ${d.severity}`}>
                                            <IconCircle stroke="0.05rem" fill={severityToColor(d.severity)}/>
                                        </Tooltip>                                        
                                        <b>{d.label}</b>
                                        <Tooltip multiline label={d.description} maw="50%">
                                            <IconHelpCircle stroke="0.1rem"/>
                                        </Tooltip>
                                        <Tooltip multiline label={d.tips} maw="50%">
                                            <IconHammer stroke="0.1rem"/>
                                        </Tooltip>
                                    </Group>
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
