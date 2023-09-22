import {
    Button,
    Checkbox,
    Container,
    createStyles,
    Flex,
    Group,
    rem,
    ScrollArea,
    Text,
    Title,
    Tooltip,
} from "@mantine/core";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { IconGripVertical, IconHelpCircle } from "@tabler/icons-react";
import { IClassifier } from "../core/models/IClassifier";

const useStyles = createStyles((theme) => ({
    item: {
        display: "flex",
        alignItems: "center",
        borderRadius: theme.radius.md,
        border: `${rem(1)} solid ${
            theme.colorScheme === "dark"
                ? theme.colors.dark[5]
                : theme.colors.gray[2]
        }`,
        padding: `${theme.spacing.sm} ${theme.spacing.xl}`,
        paddingLeft: `calc(${theme.spacing.xl} - ${theme.spacing.md})`, // to offset drag handle
        backgroundColor:
            theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.white,
        marginBottom: theme.spacing.sm,
    },

    itemDragging: {
        boxShadow: theme.shadows.sm,
    },

    dragHandle: {
        ...theme.fn.focusStyles(),
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        color:
            theme.colorScheme === "dark"
                ? theme.colors.dark[1]
                : theme.colors.gray[6],
        paddingLeft: theme.spacing.md,
        paddingRight: theme.spacing.md,
    },
}));

export type IClassifierExt = IClassifier & {
    isChecked: boolean;
};

interface PolicyMapFiltersProps {
    classifiers?: IClassifierExt[];
    toogle: (id: number) => void;
    reorder: (from: number, to: number) => void;
    next: () => void;
}

const PolicyMapFilters: React.FC<PolicyMapFiltersProps> = ({
    classifiers,
    toogle,
    reorder,
    next,
}) => {
    const { classes, cx } = useStyles();

    if (!classifiers) return null;

    const items = classifiers.map((item, index) => (
        <Draggable key={item.id} index={index} draggableId={item.id.toString()}>
            {(provided, snapshot) => (
                <div
                    className={cx(classes.item, {
                        [classes.itemDragging]: snapshot.isDragging,
                    })}
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                >
                    <div
                        {...provided.dragHandleProps}
                        className={classes.dragHandle}
                    >
                        <IconGripVertical size="1.5rem" stroke={1.5} />
                    </div>
                    <Checkbox
                        size="lg"
                        pr="1rem"
                        checked={item.isChecked}
                        onChange={() => toogle(item.id)}
                    />
                    <div>
                        <Text>{item.name}</Text>
                        <Text color="dimmed" size="sm">
                            {item.description}
                        </Text>
                    </div>
                </div>
            )}
        </Draggable>
    ));

    const showDataClick = () => {
        next();
    };

    const helpText =
        "The tool allows you to flexibly visualize the security policy defined by a set of security rules. Arbitrary multilevel grouping of nodes based on the presented set of properties is possible. You can create arbitrary multilevel groupings of nodes based on the presented properties. To perform the grouping, you need to select the required levels and establish their order. The order is set from the top to the bottom by dragging the chosen levels. A node that belongs to multiple groups will be displayed within each of those groups.";

    return (
        <Container h="100%" p="1rem 0">
            <Flex direction="column" h="100%">
                <Title order={3}>
                    <Group>
                        <Tooltip multiline label={helpText} maw="50%">
                            <IconHelpCircle stroke="0.1rem" />
                        </Tooltip>
                        Select categories and define their order
                    </Group>
                </Title>
                <ScrollArea type="auto" offsetScrollbars pt="1rem">
                    <DragDropContext
                        onDragEnd={({ destination, source }) => {
                            if (destination) {
                                reorder(source.index, destination.index);
                            }
                        }}
                    >
                        <Droppable droppableId="dnd-list" direction="vertical">
                            {(provided) => (
                                <div
                                    {...provided.droppableProps}
                                    ref={provided.innerRef}
                                >
                                    {items}
                                    {provided.placeholder}
                                </div>
                            )}
                        </Droppable>
                    </DragDropContext>
                </ScrollArea>
                <Group position="center" mt="xl">
                    <Button
                        size="lg"
                        radius="xl"
                        onClick={showDataClick}
                        disabled={classifiers.every(
                            (classifier) => !classifier.isChecked
                        )}
                    >
                        Show data
                    </Button>
                </Group>
            </Flex>
        </Container>
    );
};

export default PolicyMapFilters;
