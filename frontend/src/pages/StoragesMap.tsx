import React, { useState } from "react";
import UniversalMap from "../components/UniversalMap/UniversalMap";
import {
    ItemStyles,
    ChildrenInfo,
    findItemById,
    LayoutStyle,
} from "../components/UniversalMap/UniversalMapData";

import { HEADER_HEIGHT } from "../components/Header";
import { Alert, Loader, Text, useMantineTheme } from "@mantine/core";
import { useStorages } from "../core/hooks/storages";
import { IconAlertTriangle } from "@tabler/icons-react";

export function StoragesMap() {
    const theme = useMantineTheme();
    const isDark = theme.colorScheme === "dark";

    const styles: ItemStyles = {
        Cloud: {
            item: {
                style: {
                    margin: "1rem",
                },
            },
            header: {
                icon: "IconCloud",
            },
            layout: {
                childrenContainerStyle: {
                    border: "1px solid gray",
                    padding: "1rem",
                },
            },
        },
        Bucket: {
            item: {
                style: {
                    border: "1px solid gray",
                    padding: "0.2rem",
                    background: isDark ? theme.colors.dark[6] : theme.colors.blue[3]
                }
            },
            header: {
                maxLabelWidth: "100rem"
            },
        }
    };

    const {loading, error, data, setData} = useStorages();

    const toogleChildrens = function (id: string) {
        setData((oldData) => {
            const newData = JSON.parse(JSON.stringify(oldData));
            const item = findItemById(newData, id);
            if (item) {
                if (item.childrenCollapsed ?? false) {
                    item.childrenCollapsed = false;
                } else {
                    item.childrenCollapsed = true;
                }
            }
            return newData;
        });
    };

    const style: LayoutStyle = {
        verticalGap: "0.2rem",
    };

    return (
        <div
            style={{
                width: "100vw",
                height: `calc(100vh - ${HEADER_HEIGHT})`,
                position: "relative",
                backgroundColor: isDark ? theme.colors.gray[8] : "#F5F5DC",
            }}
        >
            {loading && (<Loader
                sx={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                }}
            />)}
            {!loading && error && ( <Alert
                icon={<IconAlertTriangle size="1rem" />}
                title="Cannot get storages"
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
            </Alert>)}
            {!loading && data && (
                <UniversalMap
                    styles={styles}
                    style={style}
                    data={data}
                    toogleChildrens={toogleChildrens}
                />
            )}
        </div>
    );
}
