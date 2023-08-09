import { px } from "@mantine/styles";
import { LineInfo } from "./UniversalMapData";
import { useLayoutEffect, useRef, useState } from "react";

type Position = {
    x: number;
    y: number;
    width: number;
    height: number;
};

type ElementInfo = {
    id: string;
    elem: HTMLElement;
    pos: Position;
    center: {
        x: number;
        y: number;
    };
};

type ExtentedInfo = {
    src: ElementInfo;
    dst: ElementInfo;
    dist2: number;
    srcDstAngle: number;
    srcAngle: number;
    dstAngle: number;
};

type ArrowInfo = {
    type: "src" | "dst";
    angle: number;
    extInfo: ExtentedInfo;
};

function getOffsetRect(
    element: HTMLElement,
    parent: HTMLElement
): Position | null {
    var el: HTMLElement = element,
        offsetLeft = 0,
        offsetTop = 0;

    do {
        offsetLeft += el.offsetLeft;
        offsetTop += el.offsetTop;

        if (!el.offsetParent || !(el.offsetParent as HTMLElement)) {
            return null;
        }
        el = el.offsetParent as HTMLElement;
    } while (el !== parent);

    return {
        x: offsetLeft,
        y: offsetTop,
        width: element.offsetWidth,
        height: element.offsetHeight,
    };
}

function calculateDist2Angle(
    c1: { x: number; y: number },
    c2: { x: number; y: number }
): number[] {
    const deltaX = c2.x - c1.x;
    const deltaY = c2.y - c1.y;
    let radians = Math.atan2(deltaY, deltaX);
    if (radians < 0) {
        radians += 2 * Math.PI;
    }
    const dist2 = deltaX * deltaX + deltaY * deltaY;
    return [dist2, radians];
}

function findIntersectionOffset(
    alpha: number,
    width: number,
    height: number
): {
    x: number;
    y: number;
} {
    var rayDirX = Math.cos(alpha);
    var rayDirY = Math.sin(alpha);

    var x1 = -width / 2,
        y1 = -height / 2;
    var x2 = width / 2,
        y2 = height / 2;

    var intersection = null;

    // top or bottom
    if (rayDirY < 0) {
        intersection = { x: (rayDirX / rayDirY) * y1 + x2, y: 0};
        if (intersection.x >= 0 && intersection.x <= width) {            
            return intersection;
        }
    } else if (rayDirY > 0) {
        intersection = { x: (rayDirX / rayDirY) * y2 + x2, y: height};
        if (intersection.x >= 0 && intersection.x <= width) {
            return intersection;
        }
    }

    // left or right
    if (rayDirX < 0) {
        intersection = { x: 0, y: (rayDirY / rayDirX) * x1 + y2};
        if (intersection.y >= 0 && intersection.y <= height) {
            return intersection;
        }
    } else if (rayDirX > 0) {
        intersection = { x: width, y: (rayDirY / rayDirX) * x2 + y2};
        if (intersection.y >= 0 && intersection.y <= height) {
            return intersection;
        }
    }

    // unreach
    return { x: 0, y: 0 };
}

interface UniversalMapLinesProps {
    lines?: LineInfo;
}

const UniversalMapLines: React.FC<UniversalMapLinesProps> = ({ lines }) => {
    const [, setRenderState] = useState(0);
    const ref = useRef<SVGSVGElement | null>(null);
    const rerender = () => {
        setRenderState((old) => old + 1);
    };

    console.log("UniversalMapLines render");

    useLayoutEffect(() => {
        console.log("UniversalMapLines useLayoutEffect");
        rerender();
    }, []);

    if (!lines) {
        return null;
    }

    let extentedInfo: ExtentedInfo[] = [];

    if (ref.current && ref.current.parentElement) {
        const container = ref.current.parentElement;

        lines.items.forEach((line) => {
            const srcElem = document.getElementById(line.src);
            const dstElem = document.getElementById(line.dst);
            if (!srcElem || !dstElem) return null;

            const srcPos = getOffsetRect(srcElem, container);
            const dstPos = getOffsetRect(dstElem, container);
            if (!srcPos || !dstPos) return null;

            const srcInfo = {
                id: line.src,
                elem: srcElem,
                pos: srcPos,
                center: {
                    x: srcPos.x + srcPos.width / 2,
                    y: srcPos.y + srcPos.height / 2,
                },
            };

            const dstInfo = {
                id: line.dst,
                elem: dstElem,
                pos: dstPos,
                center: {
                    x: dstPos.x + dstPos.width / 2,
                    y: dstPos.y + dstPos.height / 2,
                },
            };

            const [dist2, angle] = calculateDist2Angle(
                srcInfo.center,
                dstInfo.center
            );

            let srcAngle = angle;
            let dstAngle = angle + Math.PI;
            if (dstAngle >= 2 * Math.PI) {
                dstAngle -= 2 * Math.PI;
            }

            if (dist2 < px("15rem") * px("15rem")) {
                // rem in pixels
                dstAngle = srcAngle + Math.PI / 4;
                srcAngle += Math.PI / 2;
            }

            if (srcElem.contains(dstElem)) {
                srcAngle = Math.PI / 2 + Math.PI / 4;
                dstAngle = (3 * Math.PI) / 2 - Math.PI / 4;
            } else if (dstElem.contains(srcElem)) {
                dstAngle = Math.PI / 2 + Math.PI / 4;
                srcAngle = (3 * Math.PI) / 2 - Math.PI / 4;
            }

            if (srcElem === dstElem) {
                srcAngle = 0;
                dstAngle = 0;
            }

            extentedInfo.push({
                src: srcInfo,
                dst: dstInfo,
                dist2: dist2,
                srcDstAngle: angle,
                srcAngle: srcAngle,
                dstAngle: dstAngle,
            });
        });

        // collect info
        let elementsWithArrows: Record<string, ArrowInfo[]> = {};
        extentedInfo.forEach((info) => {
            // handling the source element
            if (!elementsWithArrows[info.src.id]) {
                elementsWithArrows[info.src.id] = [];
            }
            elementsWithArrows[info.src.id].push({
                type: "src",
                angle: info.srcAngle,
                extInfo: info,
            });

            // handling the destination element
            if (!elementsWithArrows[info.dst.id]) {
                elementsWithArrows[info.dst.id] = [];
            }
            elementsWithArrows[info.dst.id].push({
                type: "dst",
                angle: info.dstAngle,
                extInfo: info,
            });
        });

        for (const id in elementsWithArrows) {
            if (elementsWithArrows[id].length < 2) {
                continue;
            }

            elementsWithArrows[id].sort((a, b) => {
                if (a.type === "src") {
                    return a.extInfo.srcAngle - b.extInfo.srcAngle;
                } else {
                    return a.extInfo.dstAngle - b.extInfo.dstAngle;
                }
            });

            let maxGap = 0;
            let minGap = Number.MAX_VALUE;
            let maxGapIndex = -1;
            let arrows = elementsWithArrows[id];

            // Iterate through the array and find the largest gap
            for (let i = 1; i < arrows.length; i++) {
                const gap = arrows[i].angle - arrows[i - 1].angle;
                if (gap > maxGap) {
                    maxGap = gap;
                    maxGapIndex = i;
                }
                if (gap < minGap) {
                    minGap = gap;
                }
            }

            // Check the gap between the last and first elements, considering 2 * Math.PI period
            const gapBetweenLastAndFirst =
                2 * Math.PI - arrows[arrows.length - 1].angle + arrows[0].angle;
            if (gapBetweenLastAndFirst > maxGap) {
                maxGap = gapBetweenLastAndFirst;
                maxGapIndex = 0;
            }
            if (gapBetweenLastAndFirst < minGap) {
                minGap = gapBetweenLastAndFirst;
            }

            // Shift the array such that the largest gap is between the last and first elements
            arrows =
                maxGapIndex === 0
                    ? arrows
                    : [
                          ...arrows.slice(maxGapIndex),
                          ...arrows.slice(0, maxGapIndex),
                      ];

            if (minGap <= Math.PI / 4) {                
                // need to place arrows by equal intervals
                let newGap = maxGap / 2;

                if (
                    2 * Math.PI - maxGap >
                    ((arrows.length - 1) * Math.PI) / 4
                ) {
                    newGap = maxGap;
                }

                let currentAngle = arrows[0].angle - (maxGap - newGap) / 2;
                let dAngle = (2 * Math.PI - newGap) / (arrows.length - 1);
                if (currentAngle < 0) {
                    currentAngle -= 2 * Math.PI;
                }

                arrows.forEach((arrow) => {
                    arrow.angle = currentAngle;
                    currentAngle += dAngle;
                    if (currentAngle > 2 * Math.PI) {
                        currentAngle -= 2 * Math.PI;
                    }
                });

                arrows.forEach((arrow) => {
                    if (arrow.type === "src") {
                        arrow.extInfo.srcAngle = arrow.angle;
                    } else {
                        arrow.extInfo.dstAngle = arrow.angle;
                    }
                });
            }
        }
    }

    return (
        <svg
            ref={ref}
            style={{
                width: "100%",
                height: "100%",
                position: "absolute",
                pointerEvents: "none",
            }}
        >
            {extentedInfo.map((item, index) => {
                const srcOffset = findIntersectionOffset(item.srcAngle, item.src.pos.width, item.src.pos.height);
                const dstOffset = findIntersectionOffset(item.dstAngle, item.dst.pos.width, item.dst.pos.height);
                const srcX = item.src.pos.x + srcOffset.x;
                const srcY = item.src.pos.y + srcOffset.y;
                const dstX = item.dst.pos.x + dstOffset.x;
                const dstY = item.dst.pos.y + dstOffset.y;

                return (
                    <path
                        key={index}
                        d={`M${srcX} ${srcY} 
                        C ${srcX + 150 * Math.cos(item.srcAngle)} ${srcY + 150 * Math.sin(item.srcAngle)}, ${dstX + 150 * Math.cos(item.dstAngle)} ${dstY + 150 * Math.sin(item.dstAngle)}, ${dstX} ${dstY}`}
                        stroke="cornflowerblue"
                        strokeWidth="4"
                        strokeLinecap="round"
                        fill="transparent"
                    />
                );
            })}
        </svg>
    );
};

export default UniversalMapLines;
