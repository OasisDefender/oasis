import React, { useState } from "react";
import UniversalMapContainer from "./UniversalMapContainer";
import {
    ChildrenInfo,
    ItemStyles,
    LayoutStyle,
    LineInfo,
    LineStyles,
} from "./UniversalMapData";

import UniversalMapLines from "./UniversalMapLines";
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
    lineStyles?: LineStyles;
    selectedID?: string;
    selectedLineID?: string;
    toogleChildren?: (id: string) => void;
    select?: (id?: string) => void;
    selectLine?: (id?: string) => void;
}

const UniversalMap: React.FC<UniversalMapProps> = ({
    data,
    lines,
    style,
    styles,
    lineStyles,
    selectedID,
    selectedLineID,
    toogleChildren,
    select,
    selectLine,
}) => {
    const [linesRerenderNumber, setLinesRerenderNumber] = useState(0);
    let wasRealPanning = false;
    const onPanningStart = (
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) => {
        wasRealPanning = false;
    };
    const onPanning = (
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) => {
        wasRealPanning = true;
    };
    const onPanningStop = (
        ref: ReactZoomPanPinchRef,
        event: TouchEvent | MouseEvent
    ) => {
        if (!wasRealPanning) {
            // Tap
            if (event.target && event.target instanceof Element) {
                if (event.target.closest(".toogle-children")) {
                    // toogleChildren
                    const item = event.target.closest(".um-item");
                    if (item) {
                        toogleChildren?.(item.id);
                        setTimeout(() => {
                            setLinesRerenderNumber((old) => old + 1);
                        });
                    }
                } else {
                    const line = event.target.closest(".um-line");
                    if (line) {
                        selectLine?.(line.id);
                    } else {
                        // select item
                        const item = event.target.closest(".um-item");
                        if (item) {
                            select?.(item.id);
                        } else {
                            select?.(undefined);
                        }
                    }
                }
            }
        }
    };

    const onTransformed = (
        ref: ReactZoomPanPinchRef,
        state: {
            scale: number;
            positionX: number;
            positionY: number;
        }
    ) => {};

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
                maxScale={12}
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
                    <UniversalMapLines
                        lines={lines}
                        styles={lineStyles}
                        selectedID={selectedLineID}
                        rerenderNumber={linesRerenderNumber}
                    />
                </TransformComponent>
            </TransformWrapper>
        </>
    );
};

export default UniversalMap;
