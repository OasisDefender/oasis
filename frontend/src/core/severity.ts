export function severityToColor(severity: number) {
    if (severity === 0) 
        return "#B4FFB4";
    if (severity === 1)
        return "#FFD26E";
    if (severity === 2)
        return "#FF6937";
    return "#FF0000";
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