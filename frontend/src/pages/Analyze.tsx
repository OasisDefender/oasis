import {
    Accordion,
    Alert,
    Badge,
    Container,
    Group,
    Loader,
    Popover,
    Space,
    Table,
    Text,
    Tooltip,
} from "@mantine/core";
import { useAnalyzation } from "../core/hooks/analyzation";
import {
    IconAlertTriangle,
    IconCircle,
    IconHammer,
    IconHelpCircle,
} from "@tabler/icons-react";
import { severityToColor, severityToText } from "../core/severity";
import { useDisclosure } from "@mantine/hooks";
import { AnalyzeGroup, AnalyzeValue, AnalyzeValueObject } from "../core/models/IAnalyzation";

function jsxJoinLines(array: any[]) {
    return array.length > 0
        ? array.reduce((result, item) => (
              <>
                  {result}
                  <br />
                  {item}
              </>
          ))
        : null;
}

function AnalyzeItemCellLine(value: string | AnalyzeValueObject) {
    if (typeof value === "string") {
        return value;
    }
    return <Tooltip withArrow multiline maw="50%" label={value.hint}><span>{value.name}</span></Tooltip>
}

export function AnalyzeItemCell({ value }: { value: AnalyzeValue }) {    
    if (Array.isArray(value)) {
        return jsxJoinLines(value.map((v) => AnalyzeItemCellLine(v)));
    }
    return AnalyzeItemCellLine(value);
}

export function AnalyzeItem({
    data,
    index,
}: {
    data: AnalyzeGroup;
    index: number;
}) {
    const [severityOpened, { close: severityClose, open: severityOpen }] =
        useDisclosure(false);
    const [helpOpened, { close: helpClose, open: helpOpen }] =
        useDisclosure(false);
    const [tipsOpened, { close: tipsClose, open: tipsOpen }] =
        useDisclosure(false);

    return (
        <Accordion.Item value={index.toString()}>
            <Accordion.Control>
                <Group position="apart" spacing="xs">
                    <Group>
                        <Popover withArrow shadow="md" opened={severityOpened}>
                            <Popover.Target>
                                <IconCircle
                                    stroke="0.05rem"
                                    fill={severityToColor(data.severity)}
                                    onMouseEnter={severityOpen}
                                    onMouseLeave={severityClose}
                                />
                            </Popover.Target>
                            <Popover.Dropdown>
                                <Text size="md">{`Severity: ${severityToText(
                                    data.severity
                                )}`}</Text>
                            </Popover.Dropdown>
                        </Popover>

                        <b>{data.label}</b>

                        <Popover
                            width="30rem"
                            withArrow
                            shadow="md"
                            opened={helpOpened}
                        >
                            <Popover.Target>
                                <IconHelpCircle
                                    stroke="0.1rem"
                                    onMouseEnter={helpOpen}
                                    onMouseLeave={helpClose}
                                />
                            </Popover.Target>
                            <Popover.Dropdown>
                                <Text size="md">{data.description}</Text>
                            </Popover.Dropdown>
                        </Popover>

                        <Popover
                            width="30rem"
                            withArrow
                            shadow="md"
                            opened={tipsOpened}
                        >
                            <Popover.Target>
                                <IconHammer
                                    stroke="0.1rem"
                                    onMouseEnter={tipsOpen}
                                    onMouseLeave={tipsClose}
                                />
                            </Popover.Target>
                            <Popover.Dropdown>
                                <Text size="md">{data.tips}</Text>
                            </Popover.Dropdown>
                        </Popover>
                    </Group>
                    <Badge size="lg" variant="filled">
                        {data.data.length}
                    </Badge>
                </Group>
            </Accordion.Control>
            <Accordion.Panel>
                <Table striped>
                    <thead>
                        <tr>
                            {data.caption.map((caption, i) => (
                                <th key={i}>{caption}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.data.map((r, j) => (
                            <tr key={j}>
                                {r.map((col, i) => (
                                    <td key={i}>
                                        <AnalyzeItemCell value={col}/>
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Accordion.Panel>
        </Accordion.Item>
    );
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
                <Accordion variant="separated" multiple={true}>
                    {data.map((d, i) => (
                        <AnalyzeItem data={d} index={i} key={i} />
                    ))}
                </Accordion>
            )}
        </Container>
    );
}
