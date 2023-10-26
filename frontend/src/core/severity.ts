export function severityToColor(severity: number) {
    if (severity === 0) 
        return "#FFFFFF";
    if (severity === 1)
        return "#34BC41";
    if (severity === 2)
        return "#FFBF00";
    return "#D0312D";
}

export function severityToText(severity: number) {
    if (severity === 0) 
        return "None";
    if (severity === 1)
        return "Low";
    if (severity === 2)
        return "Medium";
    return "High";
}