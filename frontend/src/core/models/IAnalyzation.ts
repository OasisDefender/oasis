export type AnalyzeGroup = {
    label: string;
    description: string;
    severity: number;
    caption: string[];
    data: string[][][] | string[][];
};

export type IAnalyzation = AnalyzeGroup[];
