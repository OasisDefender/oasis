import { Box, Tooltip, UnstyledButton } from "@mantine/core";
import {
    ChildItem,
    DEFAULT_COLLAPSED,
    HeaderStyle,
    ItemStyle,
    ItemStyles,
    LayoutStyle,
    TypedStyle,
    mergeObjects,
} from "./UniversalMapData";
import UniversalMapContainer from "./UniversalMapContainer";
import UniversalIcon from "./UniversalIcon";
import {
    IconSquareMinus,
    IconSquarePlus,
} from "@tabler/icons-react";
import { useMemo } from "react";

interface UniversalMapChildProps {
    data: ChildItem;
    styles?: ItemStyles;
    selectedID?: string;
    toogleChildren?: (id: string) => void;
}

function hasChildWithId(item: ChildItem, selectedId: string): boolean {
    if (item.id === selectedId) {
        return true;
    }

    if (item.children && item.children.length > 0) {
        for (const child of item.children) {
            if (hasChildWithId(child, selectedId)) {
                return true;
            }
        }
    }

    return false;
}

const UniversalMapChild: React.FC<UniversalMapChildProps> = ({
    data,
    styles,
    selectedID,
    toogleChildren,
}) => {    
    const containSelected = selectedID ? hasChildWithId(data, selectedID) : false;    
    return useMemo(() => {
        const isSelected = data.id === selectedID;
        let style: TypedStyle | undefined;

        let layoutStyle: LayoutStyle | undefined;
        let itemStyle: ItemStyle | undefined;
        let headerStyle: HeaderStyle | undefined;
        
        style = styles?.[data.type ?? ""];
        if (style) {
            layoutStyle = isSelected
                ? mergeObjects(style.layout, style.layoutSelected)
                : style.layout;
            itemStyle = isSelected
                ? mergeObjects(style.item, style.itemSelected)
                : style.item;
            headerStyle = isSelected
                ? mergeObjects(style.header, style.headerSelected)
                : style.header;
        }

        const childrenExist = data.children && data.children.length > 0;
        const childrenShow = childrenExist && !(data.childrenCollapsed ?? DEFAULT_COLLAPSED);
        return (
            <div className="um-item" id={data.id} style={itemStyle?.style}>
                <div
                    className="um-header"
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        color: headerStyle?.textColor
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                        }}
                    >
                        {headerStyle?.icon && (
                            <UniversalIcon
                                name={headerStyle?.icon}
                                color={headerStyle?.iconColor}
                            />
                        )}
                        <Box
                            maw={headerStyle?.maxLabelWidth}
                            sx={{
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                            }}
                        >
                            {data.label}
                        </Box>
                    </div>
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            paddingLeft: "0.3rem",
                        }}
                    >
                        {data.info &&
                            data.info.map((item, index) => {
                                return item.tooltip ? (
                                    <Tooltip
                                        key={index}
                                        label={item.tooltip}
                                        withArrow
                                        withinPortal
                                    >
                                        <UniversalIcon
                                            name={item.icon}
                                            color={item.iconColor}
                                        />
                                    </Tooltip>
                                ) : (
                                    <UniversalIcon
                                        name={item.icon}
                                        color={item.iconColor}
                                        key={index}
                                    />
                                );
                            })}
                        {childrenExist && toogleChildren && (
                            <UnstyledButton
                                lh={0}
                                className="toogle-children"
                            >
                                {data.childrenCollapsed ?? DEFAULT_COLLAPSED ? (
                                    <IconSquarePlus color={headerStyle?.textColor}/>
                                ) : (
                                    <IconSquareMinus color={headerStyle?.textColor}/>
                                )}
                            </UnstyledButton>
                        )}
                    </div>
                </div>
                {childrenShow && (
                    <UniversalMapContainer
                        data={data}
                        style={layoutStyle}
                        styles={styles}
                        selectedID={selectedID}
                        toogleChildren={toogleChildren}
                    />
                )}
            </div>
        );
    }, [data,
        styles,
        toogleChildren,
        containSelected ? selectedID : undefined]);
};

export default UniversalMapChild;
