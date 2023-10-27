import { useState, useEffect, ReactNode } from "react";
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
    Menu,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { useLocation, matchPath, useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { Icon } from "./Icon";
import {
    IconChevronDown,
    IconLogout,
    IconMoonStars,
    IconSun,
} from "@tabler/icons-react";
export const HEADER_HEIGHT = rem(60);

type LinkItem = {
    link: string;
    label: ReactNode;
    children?: LinkItem[];
};

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
        justifyContent: "space-between",
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

    menuLink: {
        display: "block",
        lineHeight: 1,
        padding: "0.5rem 1rem",
        borderRadius: theme.radius.sm,
        textDecoration: "none",
        color:
            theme.colorScheme === "dark"
                ? theme.colors.dark[0]
                : theme.colors.gray[7],
        fontSize: theme.fontSizes.sm,
        fontWeight: 500,

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

    iconText: {
        [theme.fn.smallerThan("md")]: {
            display: "none",
        },
    },
}));

interface DropdownMenuProps {
    active: string;
    link: string;
    label: ReactNode;
    items: LinkItem[];
    setActive: (path: string) => void;
    close: () => void;
}

const DropdownMenu: React.FC<DropdownMenuProps> = ({
    active, 
    link,
    label,
    items,
    setActive,
    close,
}) => {
    const navigate = useNavigate();
    const { classes, cx } = useStyles();

    return (
        <Menu            
            trigger="hover"
            width="target"
            offset={0}
            withArrow            
        >
            <Menu.Target>
                <div className={cx(classes.link, {
                    [classes.linkActive]: items.some(item => matchPath(active, item.link)),
                })}>
                    {label}
                    <IconChevronDown size="0.75rem"  />
                </div>
            </Menu.Target>
            <Menu.Dropdown>
                {items.map((item) => (
                    <Menu.Item
                        key={item.link}
                        className={cx(classes.menuLink, {
                            [classes.linkActive]: matchPath(active, item.link),
                        })}                       
                        onClick={() => {
                            navigate(item.link);
                            setActive(item.link);
                            setTimeout(close, 100);
                        }}                        
                    >
                        {item.label}
                    </Menu.Item>
                ))}
            </Menu.Dropdown>
        </Menu>
    );
};

interface HeaderResponsiveProps {
    links: LinkItem[];
    logout?: () => void;
}

export function HeaderResponsive({ links, logout }: HeaderResponsiveProps) {
    const { colorScheme, toggleColorScheme } = useMantineColorScheme();
    const dark = colorScheme === "dark";

    const [opened, { toggle, close }] = useDisclosure(false);
    const location = useLocation();

    const [active, setActive] = useState(location.pathname);
    const { classes, cx } = useStyles();

    const items = links.map((link) => {
        if (link.children) {
            return (
                <DropdownMenu
                    key={link.link}
                    active={active}
                    link={link.link}
                    label={link.label}
                    items={link.children}
                    setActive={setActive}
                    close={close}
                />
            );
        }

        return (
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
        );
    });

    // Subscribe to location changes
    useEffect(() => {
        setActive(location.pathname);
    }, [location]);

    return (
        <Header height={HEADER_HEIGHT} className={classes.root}>
            <Flex className={classes.header} gap="xs" align="center">
                <Icon size={24} iconTextClasses={classes.iconText} />

                <Group spacing={5} className={classes.links}>
                    {items}
                </Group>

                <Group>
                    <ActionIcon
                        color={dark ? "yellow" : "blue"}
                        onClick={() => toggleColorScheme()}
                        title="Toggle color scheme"
                    >
                        {dark ? (
                            <IconSun size="1.1rem" />
                        ) : (
                            <IconMoonStars size="1.1rem" />
                        )}
                    </ActionIcon>

                    {logout && (
                        <ActionIcon
                            color={dark ? "yellow" : "blue"}
                            onClick={logout}
                            title="Logout"
                        >
                            <IconLogout size="1.1rem" />
                        </ActionIcon>
                    )}

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
