import React, { useState } from "react";
import UniversalMapContainer from "./UniversalMapContainer";
import {
    ChildrenInfo,
    ItemStyles,
    LayoutStyle,
    LineInfo,
} from "./UniversalMapData";

import UniversalMapLines from "./UniversalMapLines";
import { useXarrow } from "react-xarrows";
import {
    ReactZoomPanPinchRef,
    TransformComponent,
    TransformWrapper,
} from "react-zoom-pan-pinch";

interface UniversalMapProps {
    data: ChildrenInfo;
    lines?: LineInfo;
    style?: LayoutStyle;
    styles?: ItemStyles;
    selectedID?: string;
    toogleChildren?: (id: string) => void;
    select?: (id?: string) => void;
}

const UniversalMap: React.FC<UniversalMapProps> = ({
    data,
    lines,
    style,
    styles,
    selectedID,
    toogleChildren,
    select,
}) => {
    const [scale, setScale] = useState(1);
    const refreshArrows = useXarrow();

    let wasRealPanning = false;
    function onPanningStart(
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) {
        wasRealPanning = false;
    }
    function onPanning(
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) {
        wasRealPanning = true;
    }
    function onPanningStop(
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) {
        if (!wasRealPanning) {
            // Tap
            if (event.target && event.target instanceof Element) {
                let action: "select" | "toogleChildren" = "select";
                if (event.target.closest(".toogle-children")) {
                    action = "toogleChildren";
                }

                const item = event.target.closest(".um-item");
                if (item) {
                    const id = item.id;
                    if (action === "select") {
                        select?.(id);                        
                    } else if (action === "toogleChildren") {
                        toogleChildren?.(id);                        
                    }
                } else {
                    // tap on empty space
                    if (action === "select") {
                        select?.(undefined);
                    }
                }
            }
        }
    }

    const onTransformed = (
        ref: ReactZoomPanPinchRef,
        state: {
            scale: number;
            positionX: number;
            positionY: number;
        }
    ) => {
        setScale((oldState) => {            
            return state.scale;
        });
        refreshArrows();
    };

    return (
        <>
            <TransformWrapper
                centerOnInit={true}
                centerZoomedOut={true}
                smooth={false}
                onPanningStart={onPanningStart}
                onPanning={onPanning}
                onPanningStop={onPanningStop}
                onTransformed={onTransformed}
                wheel={{ step: 0.25 }}
                minScale={0.25}
                maxScale={3}
            >
                <TransformComponent
                    wrapperStyle={{ width: "100%", height: "100%" }}
                >
                    <UniversalMapContainer
                        data={data}
                        styles={styles}
                        style={style}
                        toogleChildren={toogleChildren}
                        selectedID={selectedID}
                    />                                        
                </TransformComponent>
                <UniversalMapLines
                        scale={scale}
                        lines={lines}
                />
            </TransformWrapper>            
        </>
    );
};

export default UniversalMap;
