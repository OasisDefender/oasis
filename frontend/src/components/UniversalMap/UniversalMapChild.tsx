import { Tooltip, UnstyledButton } from "@mantine/core";
import {
    ChildItem,
    ItemStyles,
    LayoutStyle,
    TypedStyle,
} from "./UniversalMapData";
import UniversalMap from "./UniversalMap";
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
    toogleChildrens?: (id: string) => void;
}

const UniversalMapChild: React.FC<UniversalMapChildProps> = ({
    data,
    styles,
    toogleChildrens,
}) => {
    const isSelected = false; // TODO: do

    let style: TypedStyle | undefined;
    let layoutStyle: LayoutStyle | undefined;
    if (data.type) {
        style = styles?.[data.type];
        if (style) {
            layoutStyle = isSelected
                ? { ...style.layout, ...style.layoutSelected }
                : style.layout;
        }
    }

    const childrenExist = data.children && data.children.length > 0;
    const childrenShow = childrenExist && !(data.childrenCollapsed ?? false);

    return (
        <div className="um-item" id={data.id}>
            <div
                className="um-header"
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                }}
            >
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                    }}
                >
                    {style?.header?.icon && <UniversalIcon name={style?.header?.icon} color={style?.header?.iconColor}/>}
                    {data.label}
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
                                    <UniversalIcon name={item.icon} color={item.iconColor} />
                                </Tooltip>
                            ) : (
                                <UniversalIcon name={item.icon} color={item.iconColor} key={index} />
                            );
                        })}
                    {childrenExist && toogleChildrens && (
                        <UnstyledButton
                            lh={0}
                            onClick={() => toogleChildrens(data.id)}
                        >
                            {data.childrenCollapsed ?? false ? (
                                <IconSquarePlus />
                            ) : (
                                <IconSquareMinus />
                            )}
                        </UnstyledButton>
                    )}
                </div>
            </div> 
            {childrenShow && (
                <UniversalMap
                    data={data}
                    style={layoutStyle}
                    styles={styles}
                    toogleChildrens={toogleChildrens}
                />
            )}
        </div>
    );
};

export default UniversalMapChild;
