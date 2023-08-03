import Xarrow, { Xwrapper } from "react-xarrows";
import { ChildrenInfo, LineInfo } from "./UniversalMapData";


interface UniversalMapLinesProps {
    scale?: number;
    lines?: LineInfo;    
}

const UniversalMapLines: React.FC<UniversalMapLinesProps> = ({
    scale,
    lines,
}) => {
    if (!lines) {
        return null;
    }

    return (
        <Xwrapper>
            {lines.items.map((item) => (
                <Xarrow
                    key={item.src + "->" + item.dst}
                    start={item.src}
                    end={item.dst}
                    showHead={false}
                    strokeWidth={4 * (scale ?? 1)}                    
                />
            ))}
        </Xwrapper>
    );
};

export default UniversalMapLines;
