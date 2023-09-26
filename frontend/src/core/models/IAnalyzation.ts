
export type AnalyzeValueObject = {
    name: string;
    hint: string;    
};

export type AnalyzeValueArray = (string | AnalyzeValueObject)[];

export type AnalyzeValue = string | string[] | AnalyzeValueArray;

export type AnalyzeGroup = {
    label: string;
    description: string;
    tips: string;
    severity: number;
    caption: string[];
    data: AnalyzeValue[][];
};

export type IAnalyzation = AnalyzeGroup[];
