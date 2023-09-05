from vm import OneNode
from classifier_attr_set import attr_set


class vm_tree:
    def __init__(self, sas: attr_set, info: dict):
        self.counter = 0
        self.max_level = sas.get_max_order()
        self.children = {}
        self.label = {}
        self.n_type = {}
        self.n_icon = {}
        self.vinfo = {}
        self.vicon = {}
        self.sas = sas
        self.info = info
        self.idlist_by_node = {}
        for ord in range(0, sas.get_max_order()):
            self.label[ord] = sas.get_order_caption(ord)
            self.n_type[ord] = sas.get_order_node_type(ord)
            self.n_icon[ord] = sas.get_order_node_icon(ord)

    def add_node_by_path(self, leaf_path: list, vm: OneNode):
        d = self.children
        if len(leaf_path) != self.max_level:
            # error
            return
        for key in leaf_path[:-1]:
            d = d.setdefault(key, {})
        if leaf_path[-1] not in d:
            d[leaf_path[-1]] = []
        if vm not in [leaf_path[-1]]:
            d[leaf_path[-1]].append(vm)

    def dump_tree(self):
        c = {}
        c = {
            "children": []
        }
        # XXX Internet/All ips
        i = {
            "id": "0",
            "type": "Cloud",
            "label": "0.0.0.0/0",
            "iconTooltip": "Any IP",
            "info": []
        }
        c["children"].append(i)
        for child in self.children:
            c["children"].append(self.dump_child(
                self.children[child], 0, child))
        return c

    def dump_child(self, subtree, lvl, val):
        print("lvl: " + str(lvl))
        print("subtree: " + str(subtree))
        info = self.info.get((lvl, val), [])
        l = []
        for nfo in info:
            a = nfo.get("a", "")
            v = nfo.get("v", "Unknown")
            i = nfo.get("i", "IconInfoCircle")
            l.append({"icon": i, "tooltip": f"{a}: {v}"})

        c = {
            "id": str(lvl) + "_" + str(val),
            "type": self.n_type[lvl],
            "label": str(val),
            "iconTooltip": self.label[lvl],
            "info": l,
            "children": []
        }
        if (lvl + 1) < self.max_level:
            for child in subtree:
                c["children"].append(self.dump_child(
                    subtree[child], lvl + 1, child))
        else:
            vm: OneNode
            for vm in subtree:
                self.counter += 1
                label_text = ""
                vinfo = self.sas.get_vm_info(vm)
                for info in vinfo:
                    a = info["a"]
                    v = info["v"]
                    label_text += f"{a}: {v}"
                id = "VM_" + "_" + str(vm.id) + "_" + str(self.counter)
                if self.idlist_by_node.get(vm, None) == None:
                    self.idlist_by_node[vm] = []
                self.idlist_by_node[vm].append(id)
                t = {
                    "id": id,
                    "type": "VM",
                    "label": label_text,
                    "info": [{"icon": vm.type, "tooltip": "level:" + str(lvl) + " value:" + str(val)}],
                }
                c["children"].append(t)
        return c

    def get_idlist_by_node(self):
        return self.idlist_by_node
