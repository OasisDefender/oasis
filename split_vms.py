from ipaddress import ip_network

from cloud import Cloud
from db import DB
from cloud_map import CloudMap, cloud_map_encoder
from vpc import VPC
from subnet import Subnet
from vm import VM
from rule_group import RuleGroup, get_all_rule_groups
from rule import Rule, get_all_rules
from classifiers_list import classifier


class attr_set:
    def __init__(self, classifiers: classifier = None):
        if (classifier == None):
            self.sas = []
        else:
            for item in classifiers.selected:
                self.sas.append({"class": item["class_name"], "attr": item["field"], "caption": item["caption"],
                                "type": item["node_type"], "icon": item["node_icon"], "fn": item["fn"]})

    def add_split(self, name, attribute, cap, n_type="Cloud", icon="IconInfoCircle", fn=None):
        self.sas.append({'class': name, 'attr': attribute,
                        'caption': cap, 'type': n_type, 'icon': icon, 'fn': fn})

    def get_split(self, order):
        return self.sas[order]

    def get_max_order(self):
        return len(self.sas)

    def check_class_name(self, order, cl):
        return ((type(cl).__name__) == (self.sas[order]['class']))

    def get_aval(self, order, cl):
        if self.sas[order]['fn'] == None:
            return getattr(cl, self.sas[order]['attr'])
        else:
            return getattr(cl, self.sas[order]['fn'])()

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


class split_vms:
    def __init__(self, clouds: list[Cloud], vpcs: list[VPC], sgs: list[RuleGroup], rules: list[Rule], sas: attr_set):
        # 1. make vm_id list and forward required attributes
        self.vms = {}
        for vpc in vpcs:
            cloud = None
            for cloud in clouds:
                print(vpc)
                if cloud.id == vpc.cloud_id:
                    break
                if cloud == None:
                    # error
                    print("Cloud not found for vpc")
            for subnet in vpc.subnets:
                for vm in subnet.vms:
                    # self.vms.append(vm.id)
                    for i in range(0, sas.get_max_order()):
                        res_cl = None
                        for cl in [cloud, vpc, subnet, vm]:
                            if sas.check_class_name(i, cl):
                                res_cl = cl
                                break
                        if res_cl != None:
                            val = sas.get_aval(i, res_cl)
                            self.set_val_list(vm.id, i, [val])
                        else:
                            # security group or rule
                            l = []
                            for sg in sgs:
                                if not sas.check_class_name(i, sg):
                                    break
                                if sg.if_id == vm.if_id or sg.subnet_id == subnet.name:
                                    val = sas.get_aval(i, sg)
                                    l.append(val)
                            if (len(l)) > 0:
                                self.set_val_list(vm.id, i, l)
                            l = []
                            for sg in sgs:
                                if sg.if_id != vm.if_id and sg.subnet_id != subnet.id:
                                    continue
                                for rule in rules:
                                    if not sas.check_class_name(i, rule):
                                        break
                                    if self.is_applicable(vm, rule):
                                        rlist = self.unpack_rule(rule)
                                        for r in rlist:
                                            val = sas.get_aval(i, res_cl)
                                            l.append(val)
                            if (len(l)) > 0:
                                self.set_val_list(vm.id, i, l)

    def build_vms_tree(self, sas: attr_set):
        t = vm_tree(sas)
        ord_count = sas.get_max_order()
        for vm_id in self.vms:
            leaf_count = 1
            ord_val = {}
            for ord in range(0, ord_count):
                leaf_count *= len(self.vms[vm_id][ord])
                ord_val[ord] = 0
            for i in range(0, leaf_count):
                path = []
                for j in range(0, ord_count):
                    path.append(self.vms[vm_id][j][ord_val[j]])
                t.add_node_by_path(path, vm_id)
                for j in range(0, ord_count):
                    if ord_val[j] < (len(self.vms[vm_id][ord]) - 1):
                        ord_val[j] += 1
                        for k in [0, j - 1]:
                            ord_val[k] = 0
        return t

    def is_applicable(self, vm: VM, rule: Rule):
        return True

    def set_val_list(self, vm_id, order, val_list):
        if self.vms.get(vm_id, None) == None:
            self.vms[vm_id] = {}
        self.vms[vm_id][order] = val_list

    def unpack_rule(self, r: Rule):
        l = []
        for i in range(r.port_from, r.port_to):
            t = r
            t.type = self.type_by_port(i)
            l.append(t)
        return l

    def type_by_port(port):
        if port == 80:
            return 'Web (HTTP)'
        if port == 443:
            return 'Web (HTTPS)'
        if port == 3306:
            return 'SQL Server (MySQL)'
        return port


class vm_tree:
    def __init__(self, sas: attr_set):
        self.counter = 0
        self.max_level = sas.get_max_order()
        self.children = {}
        self.label = {}
        self.n_type = {}
        self.n_icon = {}
        for ord in range(0, sas.get_max_order()):
            self.label[ord] = sas.get_order_caption(ord)
            self.n_type[ord] = sas.get_order_node_type(ord)
            self.n_icon[ord] = sas.get_order_node_icon(ord)

    def add_node_by_path(self, leaf_path: list, vm_id):
        d = self.children
        if len(leaf_path) != self.max_level:
            # error
            return
        for key in leaf_path[:-1]:
            d = d.setdefault(key, {})
        if leaf_path[-1] not in d:
            d[leaf_path[-1]] = []
        d[leaf_path[-1]].append(vm_id)

    def dump_tree(self):
        c = {}
        c = {
            "children": []
        }
        for child in self.children:
            c["children"].append(self.dump_child(
                self.children[child], 0, child))
        return c

    def dump_child(self, subtree, lvl, val):
        print("lvl: " + str(lvl))
        print("subtree: " + str(subtree))
        c = {
            "id": str(lvl) + "_" + str(val),
            "type": self.n_type[lvl],
            "label": self.label[lvl] + ":" + str(val),
            "info": [{"icon": self.n_icon[lvl], "tooltip": "level:" + str(lvl) + " value:" + str(val)}],
            "children": []
        }
        if (lvl + 1) < self.max_level:
            for child in subtree:
                c["children"].append(self.dump_child(
                    subtree[child], lvl + 1, child))
        else:
            for vm_id in subtree:
                self.counter += 1
                t = {
                    "id": "VM_" + "_" + str(vm_id) + "_" + str(self.counter),
                    "type": "VM",
                    "label": "VM_ID: " + str(vm_id),
                    "info": [{"icon": "VM", "tooltip": "level:" + str(lvl) + " value:" + str(val)}],
                }
                c["children"].append(t)
        return c


def run_test():
    sas = attr_set()
    sas.add_split("VM", "os", "OS", "VPC")
    sas.add_split("Cloud", "name", "Cloud Name", "Cloud")
    sas.add_split("VPC", "name", "VPC Name", "VPC")
    sas.add_split("RuleGroup", "name", "Security Group Name", "VPC")
#    sas.add_split("RuleGroup", "name", "Security Group Name", "VPC")

    context = DB()
    clouds = context.get_clouds()
    map = CloudMap()
    map.get()
    vpcs = map.vpcs

    sgs = get_all_rule_groups()
    rules = get_all_rules()

    vms = split_vms(clouds, vpcs, sgs, rules, sas)
    t = vms.build_vms_tree(sas)
    res = t.dump_tree()
    print(res)

    print(res)


if __name__ == '__main__':
    run_test()
