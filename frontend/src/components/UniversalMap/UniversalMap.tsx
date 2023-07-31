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
    selectedID?: string;
    toogleChildrens?: (id: string) => void;
    select?: (id?: string) => void;
}

const UniversalMap: React.FC<UniversalMapProps> = ({
    data,
    style,
    styles,
    selectedID,
    toogleChildrens,
    select
}) => {
    const spaceRef = React.useRef<ZoomSpace>(null);
    const innerDivRef = React.useRef<HTMLDivElement>(null);

    function onDecideHowToHandlePress(
        e: MouseEvent | TouchEvent,
        coordinates: PressEventCoordinates
    ): PressHandlingOptions | undefined {
        if (e.target && e.target instanceof Element) {
            if (e.target.closest("button")) {
                return { ignorePressEntirely: true };
            }

            const item = e.target.closest(".um-item");
            if (item) {                
                const id = item.id;
                return {
                    onTap() {                    
                        select?.(id);
                    },
                };
            }
        }
        return {
            onTap() {
                select?.(undefined);
            },
        };
    }

    return (
        <ZoomSpace
                ref={spaceRef}
                onDecideHowToHandlePress={onDecideHowToHandlePress}
        >
            <div style={{ position: "absolute" }} ref={innerDivRef}>
                <UniversalMapContainer
                    data={data}
                    styles={styles}
                    style={style}            
                    toogleChildrens={toogleChildrens}
                />
            </div>
        </ZoomSpace>
    );
}



export default UniversalMap;
