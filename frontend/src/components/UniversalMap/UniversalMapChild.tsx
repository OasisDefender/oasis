import { Box, Tooltip, UnstyledButton } from "@mantine/core";
import {
    ChildItem,
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
    IconMinus,
    IconSquareMinus,
    IconSquarePlus,
} from "@tabler/icons-react";
import { transitions } from "@mantine/core/lib/Transition/transitions";

interface UniversalMapChildProps {
    data: ChildItem;
    styles?: ItemStyles;
    selectedID?: string;
    toogleChildrens?: (id: string) => void;
}

const UniversalMapChild: React.FC<UniversalMapChildProps> = ({
    data,
    styles,
    selectedID,
    toogleChildrens,
}) => {
    console.log(data.id, selectedID, data.id === selectedID);
    const isSelected = data.id === selectedID;

    let style: TypedStyle | undefined;

    let layoutStyle: LayoutStyle | undefined;
    let itemStyle: ItemStyle | undefined;
    let headerStyle: HeaderStyle | undefined;
    if (data.type) {
        style = styles?.[data.type];
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
    }

    const childrenExist = data.children && data.children.length > 0;
    const childrenShow = childrenExist && !(data.childrenCollapsed ?? false);

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
                        maw={headerStyle?.maxLabelWidth ?? "10rem"}
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
                    {childrenExist && toogleChildrens && (
                        <UnstyledButton
                            lh={0}
                            onClick={() => toogleChildrens(data.id)}
                        >
                            {data.childrenCollapsed ?? false ? (
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
                    toogleChildrens={toogleChildrens}
                />
            )}
        </div>
    );
};

export default UniversalMapChild;
