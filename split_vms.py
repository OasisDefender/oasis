from ipaddress import ip_network

from cloud import Cloud
from db import DB
from cloud_map import CloudMap, cloud_map_encoder
from vpc import VPC
from subnet import Subnet
from vm import VM, Nodes, OneNode
from rule_group import RuleGroup, get_all_rule_groups
from rule import Rule, get_all_rules
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
                    {"name": item["name"], "attr": item["field"]})

    def add_split(self, name, attribute, cap, n_type="Cloud", icon="IconInfoCircle", fn=None, info=[]):
        self.sas.append({'class': name, 'attr': attribute,
                        'caption': cap, 'type': n_type, 'icon': icon, 'fn': fn})
        self.info.append(info)

    def add_vm_info(self, name, attribute):
        self.vinfo.append({"name": name, 'attr': attribute})

    def add_info(self, order, title,  attr_name, icon="IconInfoCircle"):
        if self.info.get(order, None) == None:
            self.info[order] = []
        self.info[order].append(
            {"title": title, "attr": attr_name, "icon": icon})

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
            v = getattr(cl, i['attr'])
            info.append({"a": a, "v": v})
        return info

    def get_val(self, order, cl):
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
    def __init__(self, clouds: list[Cloud], vpcs: list[VPC], subnets: list[Subnet], nodes: list[OneNode], sgs: list[RuleGroup], rules: list[Rule], sas: attr_set):
        self.vms = {}
        self.info = {}

        self.fakeCloud = Cloud(
            None, "fakeCloud", "fakeCloud", "fakeCloud", "", "", "", "", "", "")
        self.fakeVpc = VPC(None, "fakeVPC")
        self.fakeSubnet = Subnet(None, "fakeSubnet")
        self.fakeSecGroup = RuleGroup()
        self.fakeSecRule = Rule(group_id=0, action='deny')

        # cl_list = []
        t = [[*set(clouds)], [*set(vpcs)], [*set(subnets)],
             [*set(nodes)], [*set(sgs)], [*set(rules)]]
        o = []
        o_dict = {}
        for item in nodes:
            c_list = self.cloud_list(clouds, item)
            v_list = self.vpc_list(vpcs, item)
            s_list = self.subnet_list(subnets, item)
            n_list = self.nodes_list(nodes, item)
            sgs_list = self.sec_groups_list(sgs, item)
            r_list = self.sec_rules_list(rules, sgs_list, item)
            o_dict[item] = [c_list, v_list, s_list, n_list, sgs_list, r_list]

        for order in range(0, sas.get_max_order()):
            idx = self.find_class_idx(order, t, sas)
            # cl_list.append(t[idx])
            # odict = self.build_object_dict(nodes, t[idx])
            for n in nodes:
                olist = o_dict[n][idx]
                for o in olist:
                    val = sas.get_val(order, o)
                    self.add_val(n, order, val)
                    info = sas.get_info(order, o)
                    if type(val) is list:
                        for v in val:
                            self.add_info(order, v, info)
                    else:
                        self.add_info(order, val, info)

    def add_info(self, order, val, info):
        self.info[(order, val)] = info

    def find_class_idx(self, order, t: list, sas: attr_set):
        for idx in range(0, len(t)):
            if type(t[idx]) is not list:
                return None
            if len(t[idx]) == 0:
                return None
            cl = t[idx][0]
            if sas.check_class_name(order, cl):
                return idx
        return None

    def cloud_list(self, clouds: list[Cloud], n: OneNode):
        r = [c for c in clouds if c.id == n.cloud_id]
        if len(r) == 0:
            r = [self.fakeCloud]
        return r

    def vpc_list(self, vpcs: list[VPC], n: OneNode):
        r = [c for c in vpcs if c.vpc_id ==
             n.vpc_id and c.cloud_id == n.cloud_id]
        if len(r) == 0:
            r = [self.fakeVpc]
        return r

    def subnet_list(self, subnets: list[Subnet], n: OneNode):
        r = [c for c in subnets if c.name == n.subnet_id and c.cloud_id ==
             n.cloud_id and c.vpc_id == n.vpc_id]
        if len(r) == 0:
            r = [self.fakeSubnet]
        return r

    def sec_groups_list(self, sgs: list[RuleGroup], n: OneNode):
        r = [c for c in sgs if (c.cloud_id == n.cloud_id) and (
            (c.if_id == n.if_id) or (c.subnet_id == n.subnet_id))]
        if len(r) == 0:
            r = [self.fakeSecGroup]
        return r

    def sec_rules_list(self, rules: list[Rule], sec_groups: list[RuleGroup], n: OneNode):
        t = []
        for s in sec_groups:
            t.append(s.name)
        r = [c for c in rules if c.cloud_id ==
             n.cloud_id and (c.group_id in t)]
        if len(r) == 0:
            r = [self.fakeSecRule]
        return r

    def nodes_list(self, nodes: list[OneNode], n: OneNode):
        r = [n]
        return r

    def build_vms_tree(self, sas: attr_set):
        t = vm_tree(sas, self.info)
        ord_count = sas.get_max_order()
        for vm in self.vms:
            leaf_count = 1
            ord_val = {}
            for ord in range(0, ord_count):
                if self.vms[vm].get(ord, None) == None:
                    self.vms[vm][ord] = ["Non Applicable"]
                leaf_count *= len(self.vms[vm][ord])
                ord_val[ord] = 0
            for i in range(0, leaf_count):
                path = []
                for j in range(0, ord_count):
                    path.append(self.vms[vm][j][ord_val[j]])
                t.add_node_by_path(path, vm)
                for j in range(0, ord_count):
                    if ord_val[j] < (len(self.vms[vm][j]) - 1):
                        ord_val[j] += 1
                        for k in range(0, j):
                            ord_val[k] = 0
                        break
        return t

    def is_applicable(self, vm: VM, rule: Rule):
        return True

    def set_val_list(self, vm, order, val_list):
        if self.vms.get(vm, None) == None:
            self.vms[vm] = {}
        self.vms[vm][order] = val_list

    def add_val_list(self, vm, order, val_list):
        if self.vms.get(vm, None) == None:
            self.vms[vm] = {}
        if order not in self.vms[vm]:
            self.vms[vm][order] = []
        self.vms[vm][order] = [*set(self.vms[vm][order] + val_list),]

    def add_val(self, vm, order, val):
        if (type(val) is list):
            self.add_val_list(vm, order, val)
        else:
            self.add_val_list(vm, order, [val])


'''
   class split_vms:
    def __init__(self, clouds: list[Cloud], vpcs: list[VPC], sgs: list[RuleGroup], rules: list[Rule], sas: attr_set):
        # 1. make vm_id list and forward required attributes
        self.vms = {}
        self.vminfo = {}
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
                    if self.vminfo.get(vm.id, None) == None:
                        self.vminfo[vm.id] = sas.get_vm_info(vm)
                    for i in range(0, sas.get_max_order()):
                        res_cl = None
                        for cl in [cloud, vpc, subnet, vm]:
                            if sas.check_class_name(i, cl):
                                res_cl = cl
                                break
                        if res_cl != None:
                            val = sas.get_val(i, res_cl)
                            self.add_val(vm.id, i, val)
                        else:
                            # security group or rule
                            for sg in sgs:
                                if not sas.check_class_name(i, sg):
                                    break
                                if sg.if_id == vm.if_id or sg.subnet_id == subnet.name:
                                    val = sas.get_val(i, sg)
                                    self.add_val(vm.id, i, val)
                            for sg in sgs:
                                if sg.if_id != vm.if_id and sg.subnet_id != subnet.id:
                                    continue
                                for rule in rules:
                                    if rule.group_id != sg.name:
                                        continue
                                    if not sas.check_class_name(i, rule):
                                        break
                                    if self.is_applicable(vm, rule):
                                        val = sas.get_val(i, rule)
                                        self.add_val(vm.id, i, val)
'''


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
                t = {
                    "id": "VM_" + "_" + str(vm.id) + "_" + str(self.counter),
                    "type": "VM",
                    "label": label_text,
                    "info": [{"icon": vm.type, "tooltip": "level:" + str(lvl) + " value:" + str(val)}],
                }
                c["children"].append(t)
        return c


'''class vm_links:
    def __init__(self, nodes: list[OneNode], sgs: list[RuleGroup], rules: list[Rule]):
        # self.in_links = {vm:[{vm}]}}
        # self.out_links = {vm:[]}}
'''


def run_test():
    sas = attr_set()
    sas.add_split("Rule", "", "os", "VM", "IconInfoCircle", "server_type")
    # sas.add_split("OneNode", "type", "type", "VPC")
    # sas.add_split("Cloud", "name", "Cloud Name", "Cloud")
    # sas.add_split("VPC", "name", "VPC Name", "VPC")
    # sas.add_split("RuleGroup", "name", "Security Group Name", "VPC")
#    sas.add_split("RuleGroup", "name", "Security Group Name", "VPC")
    sas.add_vm_info("<BR>MAC", "mac")
    sas.add_vm_info("<BR>Name", "note")
    sas.add_vm_info("<BR>Private IP", "privip")

    context = DB()
    clouds = context.get_clouds()
    map = CloudMap()
    map.get()
    vpcs = map.vpcs

    sgs = get_all_rule_groups()
    rules = get_all_rules()
    nodes = Nodes(context.get_all_nodes_info())
    s = []
    for v in vpcs:
        s = s + v.subnets
    subnets = [*set(s)]

    vms = split_vms(clouds, vpcs, subnets, nodes.nodes, sgs, rules, sas)
    t = vms.build_vms_tree(sas)
    res = t.dump_tree()
    print(res)


if __name__ == '__main__':
    run_test()
