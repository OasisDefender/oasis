import { ReactElement } from "react";
import {
    ChildItem,
    ChildrenInfo,
    LayoutStyle,
    TypedStyle,
} from "./UniversalMapData";
import { Flex } from "@mantine/core";
import UniversalMapChild from "./UniversalMapChild";

interface UniversalMapContainerProps {
    data: ChildrenInfo;
    style?: LayoutStyle;
    styles?: { [styleName: string]: TypedStyle };
    selectedID?: string;
    toogleChildren?: (id: string) => void;
}

const UniversalMapContainer: React.FC<UniversalMapContainerProps> = ({
    data,
    style,
    styles,
    selectedID,
    toogleChildren,
}) => {
    if (!data.children || !data.children.length) {
        return null;
    }

    const childrenCount = data.children.length;

    let content: ReactElement | undefined = undefined;

    const renderChild = (child: ChildItem) => (
        <UniversalMapChild
            key={child.id}
            data={child}
            styles={styles}
            selectedID={selectedID}
            toogleChildren={toogleChildren}
        />
    );

    switch (data.childrenLayout ?? "grid") {
        case "row":
            content = (
                <Flex
                    direction="row"
                    gap={style?.horizontalGap ?? "1rem"}
                    align="center"
                >
                    {data.children.map(renderChild)}
                </Flex>
            );
            break;
        case "column":
            content = (
                <Flex
                    direction="column"
                    gap={style?.verticalGap ?? "1rem"}
                    align="center"
                >
                    {data.children.map(renderChild)}
                </Flex>
            );
            break;
        case "grid":
            const columnCount = Math.ceil(Math.sqrt(childrenCount)); // Calculate columns for square grid
            const rows = Math.ceil(childrenCount / columnCount);
            content = (
                <Flex direction="column" gap={style?.verticalGap ?? "1rem"}>
                    {Array.from({ length: rows }).map((_, rowIndex) => (
                        <Flex
                            key={rowIndex}
                            direction="row"
                            gap={style?.horizontalGap ?? "1rem"}
                            align="center"
                        >
                            {data
                                .children!.slice(
                                    rowIndex * columnCount,
                                    (rowIndex + 1) * columnCount
                                )
                                .map(renderChild)}
                        </Flex>
                    ))}
                </Flex>
            );
            break;
    }

    return (
        <div className="um-children" style={style?.childrenContainerStyle}>
            {content}
        </div>
    );
};

export default UniversalMapContainer;
