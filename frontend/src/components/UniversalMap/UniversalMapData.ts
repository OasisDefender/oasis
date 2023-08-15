// Styles

import { SystemProp, SpacingValue } from "@mantine/core";
import { CSSProperties } from "react";

export type ItemStyle = {
    style?: CSSProperties;
    childrenContainerStyle?: CSSProperties;
};

export type LayoutStyle = {
    verticalGap?: SystemProp<SpacingValue>;
    horizontalGap?: SystemProp<SpacingValue>;
    childrenContainerStyle?: CSSProperties;
};

export type HeaderStyle = {
    icon?: string;
    iconColor?: string;
    textColor?: string;
    maxLabelWidth?: SystemProp<CSSProperties["maxWidth"]>;
};

export type TypedStyle = {
    item?: ItemStyle;
    itemSelected?: ItemStyle;
    layout?: LayoutStyle;
    layoutSelected?: LayoutStyle;
    header?: HeaderStyle;
    headerSelected?: HeaderStyle;
};

export type ItemStyles = { [styleName: string]: TypedStyle };


export type LineStyle = {
    gravity?: number;
    stroke?: string;
    strokeWidth?: number | string;
    strokeOpacity?: number | string;
};

export type TypedLineStyle = {
    line?: LineStyle;
    lineSelected?: LineStyle;
}

export type LineStyles = { [styleName: string]: TypedLineStyle };

// Data

export type Layout = "row" | "column" | "grid";

export type ChildrenInfo = {
    children?: ChildItem[];
    childrenLayout?: Layout;
};

export type ChildItem = ChildrenInfo & {
    id: string;
    type?: string;
    label?: string;
    info?: InfoItem[];
    childrenCollapsed?: boolean;
};

export const DEFAULT_COLLAPSED : boolean = true;

export type InfoItem = {
    icon: string;
    iconColor?: string;
    tooltip?: string;
};

// Lines
export type LineItem = {
    id?: string;
    type?: string;
    src: string;
    dst: string;    
    srcTooltip?: string;
    dstTooltip?: string;
};

export type LineInfo = {
    items: LineItem[];
};


// Functions

export function findItemById(data: ChildrenInfo, id: string): ChildItem | null {
    let result: ChildItem | null = null;

    function traverse(children: ChildItem[] | undefined) {
        if (!children) return;
        for (const child of children) {
            if (child.id === id) {
                result = child;
                return;
            }
            if (child.children) {
                traverse(child.children);
            }
            if (result) return; // Found the item, stop the loop
        }
    }
    traverse(data.children);
    return result;
}

export function findItemAndParentsById(
    data: ChildrenInfo,
    id: string
): { elem: ChildItem | null; parents: ChildItem[] } {
    const parents: ChildItem[] = [];
    let result: ChildItem | null = null;

    function traverse(children: ChildItem[] | undefined, parents: ChildItem[]) {
        if (!children) return;
        for (const child of children) {
            if (child.id === id) {
                result = child;
                return;
            }
            parents.push(child);
            if (child.children) {
                traverse(child.children, parents);
            }
            if (result) return;
            parents.pop();
        }
    }
    traverse(data.children, parents);
    return { elem: result, parents: [...parents] };
}

export function mergeObjects(obj1: any, obj2: any): any {
    if (
        typeof obj1 !== "object" ||
        typeof obj2 !== "object" ||
        obj1 === null ||
        obj2 === null
    ) {
        return obj2 === undefined ? obj1 : obj2;
    }

    const mergedObj: any = { ...obj1 };

    for (const key in obj2) {
        if (obj2.hasOwnProperty(key)) {
            mergedObj[key] = mergeObjects(obj1[key], obj2[key]);
        }
    }

    return mergedObj;
}

export function mergeObjectsRecursively(objects: any[]): any {
    if (objects.length === 0) {
        return {};
    }

    const mergedObject = objects.reduce(
        (acc, obj) => mergeObjects(acc, obj),
        {}
    );

    return mergedObject;
}
