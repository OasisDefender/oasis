import { useState, useEffect } from "react";
import {
    createStyles,
    Header,
    Flex,
    Group,
    Burger,
    Paper,
    Transition,    
    rem,
    useMantineColorScheme,
    ActionIcon,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { useLocation, matchPath } from "react-router-dom";
import { Link } from "react-router-dom";
import { Icon } from "./Icon";
import { IconMoonStars, IconSun } from "@tabler/icons-react";

export const HEADER_HEIGHT = rem(60);

const useStyles = createStyles((theme) => ({
    root: {
        position: "relative",
        zIndex: 1,
    },

    dropdown: {
        position: "absolute",
        top: HEADER_HEIGHT,
        left: 0,
        right: 0,
        zIndex: 0,
        borderTopRightRadius: 0,
        borderTopLeftRadius: 0,
        borderTopWidth: 0,
        overflow: "hidden",

        [theme.fn.largerThan("sm")]: {
            display: "none",
        },
    },

    header: {
        height: "100%",
        padding: "0 1rem 0 1rem",
        justifyContent: "space-between"        
    },

    links: {
        [theme.fn.smallerThan("sm")]: {
            display: "none",
        },
    },

    burger: {
        [theme.fn.largerThan("sm")]: {
            display: "none",
        },
    },

    link: {
        display: "block",
        lineHeight: 1,
        padding: `${rem(8)} ${rem(12)}`,
        borderRadius: theme.radius.sm,
        textDecoration: "none",
        color:
            theme.colorScheme === "dark"
                ? theme.colors.dark[0]
                : theme.colors.gray[7],
        fontSize: theme.fontSizes.sm,
        fontWeight: 500,

        "&:hover": {
            backgroundColor:
                theme.colorScheme === "dark"
                    ? theme.colors.dark[6]
                    : theme.colors.gray[0],
        },

        [theme.fn.smallerThan("sm")]: {
            borderRadius: 0,
            padding: theme.spacing.md,
        },
    },

    linkActive: {
        "&, &:hover": {
            backgroundColor: theme.fn.variant({
                variant: "light",
                color: theme.primaryColor,
            }).background,
            color: theme.fn.variant({
                variant: "light",
                color: theme.primaryColor,
            }).color,
        },
    },
}));

interface HeaderResponsiveProps {
    links: { link: string; label: string }[];
}

export function HeaderResponsive({ links }: HeaderResponsiveProps) {
    const { colorScheme, toggleColorScheme } = useMantineColorScheme();
    const dark = colorScheme === 'dark';

    const [opened, { toggle, close }] = useDisclosure(false);
    const location = useLocation();

    const [active, setActive] = useState(location.pathname);
    const { classes, cx } = useStyles();

    const items = links.map((link) => (
        <Link
            key={link.link}
            to={link.link}
            className={cx(classes.link, {
                [classes.linkActive]: matchPath(active, link.link),
            })}
            onClick={(event) => {
                setActive(link.link);
                close();
            }}
        >
            {link.label}
        </Link>
    ));

    // Subscribe to location changes
    useEffect(() => {
        setActive(location.pathname);
    }, [location]);    
  
    return (
        <Header height={HEADER_HEIGHT} className={classes.root}>
            <Flex className={classes.header} gap="xs" align="center">
                <Icon size={24}/>

                <Group spacing={5} className={classes.links}>
                    {items}
                </Group>

                <Group>
                    <ActionIcon
                        color={dark ? 'yellow' : 'blue'}
                        onClick={() => toggleColorScheme()}
                        title="Toggle color scheme"
                        >
                        {dark ? <IconSun size="1.1rem" /> : <IconMoonStars size="1.1rem" />}
                    </ActionIcon>

                    <Burger
                        opened={opened}
                        onClick={toggle}
                        className={classes.burger}
                        size="sm"
                    />
                </Group>

                <Transition
                    transition="pop-top-right"
                    duration={200}
                    mounted={opened}
                >
                    {(styles) => (
                        <Paper
                            className={classes.dropdown}
                            withBorder
                            style={styles}
                        >
                            {items}
                        </Paper>
                    )}
                </Transition>
            </Flex>
        </Header>
    );
}
