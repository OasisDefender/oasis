import Xarrow, { Xwrapper } from "react-xarrows";
import { ILink } from "../core/models/ILinks";
import { MapSelection } from "./MapCommon";
import React from "react";

interface MapLinesProps {
    from?: MapSelection;
    lines: ILink[];
    zoomFactor: number;
}

interface LineInfo {
    src: HTMLElement;
    dst: HTMLElement;
    srcText: string;
    dstText: string;
}

export function MapLines({ from, lines, zoomFactor }: MapLinesProps) {
    if (!from) {
        return null;
    }

    // Find arrow source
    let srcElem: HTMLElement | null = null;
    if (from.type === "network") {
        const query = `.map-network[data-id*="${from.key}"]`;
        srcElem = document.querySelector(query);
    } else {
        const id = `map_${from.type}${from.key}`;
        srcElem = document.getElementById(id);
    }
    if (!srcElem) {
        console.log("MapLines: no srcElem");
        return null;
    }

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
            console.log("MapLines: dstElem cannot be find for", line);
        } else {
            lineInfo.push({
                src: srcElem!,
                dst: dstElem,
                srcText: line.outbound,
                dstText: line.inbound
            });
        }
    });

    return (
        <Xwrapper>
            {lineInfo.map((l) => (
                <Xarrow
                    start={l.src.id}
                    end={l.dst.id}
                    showHead={false}
                    labels={{start: l.srcText, end: l.dstText}}
                    showTail={false}
                    strokeWidth={4 * zoomFactor}
                    divContainerStyle={{
                        transform: `scale(${1 / zoomFactor})`,
                    }}                    
                    passProps={{style: { cursor: "pointer" }}}
                />
            ))}
        </Xwrapper>
    );

    return (
        <Xwrapper>
            <Xarrow
                start="map_vm5"
                startAnchor={{
                    position: "middle",
                    offset: { x: 70 * zoomFactor, y: 13 * zoomFactor },
                }}
                end="map_subnet11"
                endAnchor="bottom"
                showHead={false}
                showTail={false}
                _cpx1Offset={200 * zoomFactor}
                _cpy1Offset={-200 * zoomFactor}
                _cpx2Offset={200 * zoomFactor}
                _cpy2Offset={200 * zoomFactor}
                strokeWidth={4 * zoomFactor}
                divContainerStyle={{ transform: `scale(${1 / zoomFactor})` }}
            />
        </Xwrapper>
    );
}
