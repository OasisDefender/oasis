import Xarrow, { Xwrapper } from "react-xarrows";
import { ILink } from "../core/models/ILinks";
import { MapSelection } from "./MapCommon";
import React, { useState } from "react";
import { IconZoomMoney } from "@tabler/icons-react";
import { Paper, Text } from "@mantine/core";

interface MapLinesProps {
    from?: MapSelection;
    lines: ILink[];
    zoomFactor: number;
    selectedIndex: number;
}

type Point = {
    x: number;
    y: number;
};

// Element info with zoom fix
interface ElementInfo {
    elem: HTMLElement;
    clientRect: DOMRect;
    width: number;
    height: number;
    centerX: number;
    centerY: number;
}

interface LineInfo {
    src: ElementInfo;
    dst: ElementInfo;

    dstOffset: Point;
    srcOffset: Point;

    srcText: string[];
    dstText: string[];

    srcDstAngle: number;
    srcDstDist: number;
    srcAngle: number;
    dstAngle: number;
}

function getElementInfo(element: HTMLElement, zoomFactor: number): ElementInfo {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    return {
        elem: element,
        clientRect: rect,
        width: rect.width / zoomFactor,
        height: rect.height / zoomFactor,
        centerX: centerX / zoomFactor,
        centerY: centerY / zoomFactor,
    };
}

// Calculate the angle between two points in degrees
function calculateAngle(element1: ElementInfo, element2: ElementInfo): number {
    const deltaX = element2.centerX - element1.centerX;
    const deltaY = element2.centerY - element1.centerY;
    let radians = Math.atan2(deltaY, deltaX);
    if (radians < 0) {
        radians += 2 * Math.PI;
    }
    return radians;
}

function calculateDistance(
    element1: ElementInfo,
    element2: ElementInfo
): number {
    let y = element2.centerX - element1.centerX;
    let x = element2.centerY - element1.centerY;

    return Math.sqrt(x * x + y * y);
}

function findIntersection(alpha: number, element: ElementInfo): Point {
    var rayDirX = Math.cos(alpha);
    var rayDirY = Math.sin(alpha);

    var x1 = -element.clientRect.width / 2,
        y1 = -element.clientRect.height / 2;
    var x2 = element.clientRect.width / 2,
        y2 = element.clientRect.height / 2;

    var intersection = null;

    // top or bottom
    if (rayDirY < 0) {
        intersection = { x: (rayDirX / rayDirY) * (y1 - 0) + 0, y: y1 };
        if (intersection.x >= x1 && intersection.x <= x2) {
            return intersection;
        }
    } else if (rayDirY > 0) {
        intersection = { x: (rayDirX / rayDirY) * (y2 - 0) + 0, y: y2 };
        if (intersection.x >= x1 && intersection.x <= x2) {
            return intersection;
        }
    }

    // left or right
    if (rayDirX < 0) {
        intersection = { x: x1, y: (rayDirY / rayDirX) * (x1 - 0) + 0 };
        if (intersection.y >= y1 && intersection.y <= y2) {
            return intersection;
        }
    } else if (rayDirX > 0) {
        intersection = { x: x2, y: (rayDirY / rayDirX) * (x2 - 0) + 0 };
        if (intersection.y >= y1 && intersection.y <= y2) {
            return intersection;
        }
    }

    // unreach
    return { x: 0, y: 0 };
}

export function MapLines({
    from,
    lines,
    selectedIndex,
    zoomFactor,
}: MapLinesProps) {
    const [hoverIndex, setHoverIndex] = useState(-1);

    if (!from || !lines.length) {
        return null;
    }

    // Find arrow source
    let srcElemS: HTMLElement | null = null;
    if (from.type === "network") {
        const query = `.map-network[data-id*="${from.key}"]`;
        srcElemS = document.querySelector(query);
    } else {
        const id = `map_${from.type}${from.key}`;
        srcElemS = document.getElementById(id);
    }
    if (!srcElemS) {
        console.log("MapLines: no srcElem");
        return null;
    }
    let srcElem: HTMLElement = srcElemS;

    // Find arrow destinations and create lineinfo
    let lineInfo: LineInfo[] = [];
    lines.forEach((line) => {
        let dstElem: HTMLElement | null = null;
        if (line.to.type === "network") {
            const query = `.map-network[data-id*="${line.to.address}"]`;
            dstElem = document.querySelector(query);
        } else {
            const id = `map_${line.to.type}${line.to.id}`;
            dstElem = document.getElementById(id);
        }
        if (!dstElem) {
            console.log(
                "MapLines: dstElem cannot be find from ",
                from,
                "to",
                line
            );
        } else {
            const srcInfo = getElementInfo(srcElem, zoomFactor);
            const dstInfo = getElementInfo(dstElem, zoomFactor);

            let info: LineInfo = {
                src: srcInfo,
                dst: dstInfo,
                srcText: line.inbound ? line.inbound.split(",") : [],
                dstText: line.outbound ? line.outbound.split(",") : [],
                srcDstAngle: calculateAngle(srcInfo, dstInfo),
                srcDstDist: calculateDistance(srcInfo, dstInfo),
                srcAngle: 0,
                dstAngle: 0,
                dstOffset: {
                    x: 0,
                    y: 0,
                },
                srcOffset: {
                    x: 0,
                    y: 0,
                },
            };
            info.srcAngle = info.srcDstAngle;

            // special cases
            if (info.srcDstDist < 200) {
                info.dstAngle = info.srcAngle + Math.PI / 4;
                info.srcAngle += Math.PI / 2;
            } else {
                if (line.to.type === "network") {
                    info.dstAngle = (3 * Math.PI) / 2;
                } else {
                    info.dstAngle = info.srcAngle + Math.PI;
                }
            }

            lineInfo.push(info);
        }
    });

    // sort by angle
    lineInfo.sort((a, b) => a.srcAngle - b.srcAngle);
    console.log(lineInfo);

    let maxGap = 0.0;
    let maxGapPos = 0.0;
    if (lineInfo.length > 1) {
        maxGap =
            lineInfo[0].srcAngle -
            (2 * Math.PI - lineInfo[lineInfo.length - 1].srcAngle);
        maxGapPos = 0;
        for (let i = 1; i < lineInfo.length; i++) {
            let gap = lineInfo[i].srcAngle - lineInfo[i - 1].srcAngle;
            if (gap > maxGap) {
                maxGapPos = i;
                maxGap = gap;
            }
        }
    }
    let newGap = maxGap / 3;
    console.log("maxGap", maxGap, "newGap", newGap);

    let delta = (2 * Math.PI - newGap) / lineInfo.length;
    let start = lineInfo[maxGapPos].srcAngle - newGap / 2;
    if (start < 0) {
        start = start + 2 * Math.PI;
    }

    let i = maxGapPos;
    let iteration = 0;
    do {
        lineInfo[i].srcAngle = start + delta * iteration;
        if (lineInfo[i].srcAngle > 2 * Math.PI) {
            lineInfo[i].srcAngle -= 2 * Math.PI;
        }
        i = i + 1;
        if (i === lineInfo.length) {
            i = 0;
        }
        iteration = iteration + 1;
    } while (i !== maxGapPos);

    lineInfo.forEach((l) => {
        // Find the intersection points
        const intersectionSrc = findIntersection(l.srcAngle, l.src);
        const intersectionDst = findIntersection(l.dstAngle, l.dst);

        // Compute offsets
        l.srcOffset = {
            x: intersectionSrc.x,
            y: intersectionSrc.y,
        };
        l.dstOffset = {
            x: intersectionDst.x,
            y: intersectionDst.y,
        };
    });

    let info: LineInfo | undefined = undefined;
    let srcPaperStyle: React.CSSProperties | undefined = undefined;
    let dstPaperStyle: React.CSSProperties | undefined = undefined;

    if (hoverIndex >= 0 && lineInfo.length > hoverIndex) {
        info = lineInfo[hoverIndex];
    }
    else {
        if (selectedIndex >= 0 && lineInfo.length > selectedIndex) {
            info = lineInfo[selectedIndex];
        }
    }

    if (info) {
        srcPaperStyle = {
            position: "absolute",
            left:
                info.src.elem.offsetLeft +
                info.src.width / 2 +
                info.srcOffset.x / zoomFactor,
            top:
                info.src.elem.offsetTop +
                info.src.height / 2 +
                info.srcOffset.y / zoomFactor,
            pointerEvents: "none",
        };
        dstPaperStyle = {
            position: "absolute",
            left:
                info.dst.elem.offsetLeft +
                info.dst.width / 2 +
                info.dstOffset.x / zoomFactor,
            top:
                info.dst.elem.offsetTop +
                info.dst.height / 2 +
                info.dstOffset.y / zoomFactor,
            pointerEvents: "none",
        };
        if (info.src.centerX <= info.dst.centerX) {
            srcPaperStyle.transform =
                "translateX(-100%) translateX(-5px) translateY(-50%)";
            dstPaperStyle.transform = "translateX(5px) translateY(-50%)";
        } else {
            srcPaperStyle.transform = "translateX(5px) translateY(-50%)";
            dstPaperStyle.transform =
                "translateX(-100%) translateX(-5px) translateY(-50%)";
        }
    }

    return (
        <>
            <Xwrapper>
                {lineInfo.map((l, index) => (
                    <Xarrow
                        key={index}
                        color={
                            selectedIndex === index
                                ? "cornflowerblue"
                                : hoverIndex === index
                                ? "orange"
                                : "gray"
                        }
                        start={l.src.elem.id}
                        end={l.dst.elem.id}
                        startAnchor={{
                            position: "middle",
                            offset: l.srcOffset,
                        }}
                        endAnchor={{
                            position: "middle",
                            offset: l.dstOffset,
                        }}
                        showHead={false}
                        showTail={false}
                        strokeWidth={4 * zoomFactor}
                        divContainerStyle={{
                            transform: `scale(${1 / zoomFactor})`,
                        }}
                        divContainerProps={{
                            data: index.toString(),
                            className: "map-arrow",
                        }}
                        arrowBodyProps={{
                            onMouseEnter: (e) => {
                                setHoverIndex(index);
                            },
                            onMouseLeave: (e) => {
                                if (hoverIndex === index) {
                                    setHoverIndex(-1);
                                }
                            },
                        }}
                        passProps={{ style: { cursor: "pointer" } }}
                        _cpx1Offset={100 * Math.cos(l.srcAngle) * zoomFactor}
                        _cpy1Offset={100 * Math.sin(l.srcAngle) * zoomFactor}
                        _cpx2Offset={100 * Math.cos(l.dstAngle) * zoomFactor}
                        _cpy2Offset={100 * Math.sin(l.dstAngle) * zoomFactor}
                    />
                ))}
            </Xwrapper>
            {info && info.srcText.length > 0 && (
                <Paper style={srcPaperStyle} p="xs" shadow="xs">
                    {info.srcText.map((s) => (
                        <Text>{s}</Text>
                    ))}
                </Paper>
            )}
            {info && info.dstText.length > 0 && (
                <Paper style={dstPaperStyle} p="xs" shadow="xs">
                    {info.dstText.map((s) => (
                        <Text>{s}</Text>
                    ))}
                </Paper>
            )}
        </>
    );
}
