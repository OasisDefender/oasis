// Styles

import { SystemProp, SpacingValue } from "@mantine/core";
import { CSSProperties } from "react";

export type ItemStyle = {
    childrenContainerStyle?: CSSProperties;
}

export type LayoutStyle = {
    verticalGap?: SystemProp<SpacingValue>;
    horizontalGap?: SystemProp<SpacingValue>;
    childrenContainerStyle?: CSSProperties;
}

export type HeaderStyle = {
    icon?: string;
    iconColor?: string;
}



export type TypedStyle = {
    item?: ItemStyle; 
    itemSelected?: ItemStyle;
    layout?: LayoutStyle;
    layoutSelected?: LayoutStyle;
    header?: HeaderStyle;
    headerSelected?: HeaderStyle;
};

export type ItemStyles = { [styleName: string]: TypedStyle };

// Data

export type Layout =
    | "row"
    | "column"
    | "grid";

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

export type InfoItem = {
    icon: string;
    iconColor?: string;
    tooltip?: string;
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
};

export function findItemAndParentsById(data: ChildrenInfo, id: string): {elem: ChildItem | null, parents: ChildItem[] } {
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
    return {elem: result, parents: [...parents]};
};

