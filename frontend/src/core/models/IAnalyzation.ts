export type AnalyzeGroup = {
    label: string;
    caption: string[];
    data: string[][][] | string[][];
};

export type IAnalyzation = AnalyzeGroup[];
