import React from "react";
import UniversalMapContainer from "./UniversalMapContainer";
import { ChildrenInfo, ItemStyles, LayoutStyle } from "./UniversalMapData";

import {
    PressEventCoordinates,
    PressHandlingOptions,
    Space as ZoomSpace,
} from "react-zoomable-ui";

interface UniversalMapProps {
    data: ChildrenInfo;
    style?: LayoutStyle;
    styles?: ItemStyles;
    toogleChildrens?: (id: string) => void;
}

const UniversalMap: React.FC<UniversalMapProps> = ({
    data,
    style,
    styles,
    toogleChildrens,
}) => {
    const spaceRef = React.useRef<ZoomSpace | null>(null);

    return (
        <ZoomSpace
                ref={spaceRef}
        >
            <UniversalMapContainer
                data={data}
                styles={styles}
                style={style}            
                toogleChildrens={toogleChildrens}
            />
        </ZoomSpace>
    );
}



export default UniversalMap;
