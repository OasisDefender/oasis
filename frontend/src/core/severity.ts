export function severityToColor(severity: number) {
    if (severity === 0) 
        return "#028A0F";
    if (severity === 1)
        return "#FDFD96";
    if (severity === 2)
        return "#FFBF00";
    return "#D0312D";
}