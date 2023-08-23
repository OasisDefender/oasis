import {
    Button,
    Checkbox,
    Container,
    createStyles,
    Group,
    rem,
    ScrollArea,
    Text,
    Title,
} from "@mantine/core";
import { useListState } from "@mantine/hooks";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { IconGripVertical } from "@tabler/icons-react";
import { IClassifier } from "../core/models/IClassifier";
import { useEffect, useState } from "react";

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

    symbol: {
        fontSize: rem(30),
        fontWeight: 700,
        width: rem(60),
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

interface PolicyMapFiltersProps {
    classifiers?: IClassifier[];
    showData: (classifiersIds: number[]) => void;
}

const PolicyMapFilters: React.FC<PolicyMapFiltersProps> = ({
    classifiers,
    showData,
}) => {
    const { classes, cx } = useStyles();
    const [state, handlers] = useListState(classifiers);
    const [checkedMap, setCheckedMap] = useState<{ [id: number]: boolean }>(
        () => {
            const initialCheckedMap: { [id: number]: boolean } = {};
            if (classifiers) {
                classifiers.forEach((classifier) => {
                    initialCheckedMap[classifier.id] = false;
                });
            }
            return initialCheckedMap;
        }
    );

    useEffect(() => {
        if (classifiers) {
            handlers.setState(classifiers);
            setCheckedMap(
                classifiers.reduce((map, classifier) => {
                    map[classifier.id] = false;
                    return map;
                }, {} as { [id: number]: boolean })
            );
        } else {
            handlers.setState([]);
            setCheckedMap({});
        }
    }, [classifiers]);

    if (!classifiers) return null;

    const handleCheckboxChange = (id: number) => {
        setCheckedMap((prevCheckedMap) => ({
            ...prevCheckedMap,
            [id]: !prevCheckedMap[id],
        }));
    };

    const items = state.map((item, index) => (
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
                        checked={checkedMap[item.id]}
                        onChange={() => handleCheckboxChange(item.id)}
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
        let data: number[] = [];
        state.forEach((item) => {
            if (checkedMap[item.id]) {
                data.push(item.id);
            }
        });
        showData(data);
    };

    return (
        <ScrollArea h="100%" type="auto" offsetScrollbars pt="1rem">
            <Container>
                <Title order={2}>
                    Configure the order in which the data is grouped
                </Title>
                <DragDropContext
                    onDragEnd={({ destination, source }) => {
                        if (destination) {
                            handlers.reorder({
                                from: source.index,
                                to: destination.index,
                            });
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
                <Group position="center" mt="xl">
                    <Button
                        size="lg"
                        radius="xl"
                        onClick={showDataClick}
                        disabled={
                            !Object.values(checkedMap).some(
                                (value) => value === true
                            )
                        }
                    >
                        Show data
                    </Button>
                </Group>
            </Container>
        </ScrollArea>
    );
};

export default PolicyMapFilters;
