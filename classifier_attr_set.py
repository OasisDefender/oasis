from classifiers_list import classifier, vminfo


class attr_set:
    def __init__(self, classifiers: classifier = None, vm_fields: vminfo = None):
        self.sas = []
        self.vinfo = []
        self.info = []
        if (classifiers != None):
            for item in classifiers.selected:
                self.sas.append({"class": item["class_name"], "attr": item["field"], "caption": item["description"],
                                "type": item["node_type"], "icon": item["node_icon"], "fn": item["fn"]})
                self.info.append(item["info"])
        if (vm_fields != None):
            for item in vm_fields.selected:
                self.vinfo.append(
                    {"name": item["name"], "attr": item["field"], "fn": item["fn"]})

    def add_split(self, name, attribute, cap, n_type="Cloud", icon="IconInfoCircle", fn=None, info=[]):
        self.sas.append({'class': name, 'attr': attribute,
                        'caption': cap, 'type': n_type, 'icon': icon, 'fn': fn})
        self.info.append(info)

    def add_vm_info(self, name, attribute, fn):
        self.vinfo.append({"name": name, 'attr': attribute, 'fn': fn})

    def add_info(self, order, title,  attr_name, fn, icon="IconInfoCircle"):
        if self.info.get(order, None) == None:
            self.info[order] = []
        self.info[order].append(
            {"title": title, "attr": attr_name, 'fn': fn, "icon": icon})

    def get_info(self, order, cl):
        info = []
        for item in self.info[order]:
            a = item["title"]
            i = item.get("icon", "IconInfoCircle")
            v = getattr(cl, item['attr'])
            info.append({"a": a, "v": v, "i": i})
        return info

    def get_split(self, order):
        return self.sas[order]

    def get_max_order(self):
        return len(self.sas)

    def check_class_name(self, order, cl):
        return ((type(cl).__name__) == (self.sas[order]['class']))

    def get_vm_info(self, cl):
        info = []
        for i in self.vinfo:
            a = i["name"]
            v = self.get_cl_val(cl, i['attr'], i['fn'])
            info.append({"a": a, "v": v})
        return info

    def get_val_by_order(self, order, cl):
        return self.get_cl_val(cl, self.sas[order]['attr'], self.sas[order]['fn'])

    def get_cl_val(self, cl, attr, fn):
        if attr != None:
            return getattr(cl, attr)
        if fn != None:
            return getattr(cl, fn)()
        return None

    def get_order_caption(self, order):
        if order < len(self.sas):
            return self.sas[order]['caption']
        return None

    def get_order_node_type(self, order):
        if order < len(self.sas):
            return self.sas[order]['type']
        return None

    def get_order_node_icon(self, order):
        if order < len(self.sas):
            return self.sas[order]['icon']
        return None
