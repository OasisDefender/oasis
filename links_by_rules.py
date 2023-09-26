from subnet import Subnet
from vm import OneNode
from rule_group import RuleGroup, RuleGroupNG, convert_RuleGroup_to_NG
from rule import Rule
from classifiers_list import classifier, vminfo
from ipaddress import ip_network, ip_address
from cloud import Cloud
from vpc import VPC


class links_by_rules:
    def __init__(self, clouds: list[Cloud], nodes: list[OneNode], subnets: list[Subnet], sgs1: list[RuleGroup], rules: list[Rule]):
        self.sgs_NG = convert_RuleGroup_to_NG(sgs1, rules)
        self.clouds = clouds
        self.nodes = nodes
        self.subnets = subnets
        self.rules = rules
        self.links = set()
        self.links_info = {}
        self.onesided_links = set()
        self.onesided_links_info = {}
        self.used_r = set()
        self.ext_things = set()
        self.analyze_results = []
        self.all_from_ports_rules = []
        self.all_from_ip_rules = []
        self.all_to_ports_rules = []
        self.all_to_ip_rules = []
        self.duplicate_rules = []
        self.asymetric_rules = []
        self.lonley_nodes = []
        self.unused_sgs = []
        (self.servers, self.clients) = self.build_servers_clients_rule_dict(
            self.sgs_NG, rules)
        self.nodes_by_sg = self.build_nodes_by_sg_dict()
        self.sglist_by_node = self.build_sglist_by_node_dict()

        self.analyzer_cfg = [
            {
                "label": "Rules from ANY IPs",
                "description": "Except for public resources, unrestricted connection from ANY (0.0.0.0) address is considered bad practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_from_ANY_IPs,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_from_ip_rules,
                "severity": 2
            },
            {
                "label": "Rules to ANY IPs",
                "description": "Unrestricted connection to ANY (0.0.0.0) address in general is not a recommended practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_to_ANY_IPs,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_to_ip_rules,
                "severity": 1
            },
            {
                "label": "Rules from ANY Ports",
                "description": "Granting permission to open connections from any port in general is not a recommended practice.",
                "tips": "If possible, limit the range of ports in the security rules.",
                "detect_fn": self.detect_from_ANY_ports,
                "dump_fn": self.dump_ALL_PORTS_rules,
                "data": self.all_from_ports_rules,
                "severity": 1
            },
            {
                "label": "Rules to ANY Ports",
                "description": "Except for special cases where the node acts as a NAT or Gateway, opening all ports on the node is not a recommended practice.",
                "tips": "If possible, limit the range of ports in the security rules.",
                "detect_fn": self.detect_to_ANY_ports,
                "dump_fn": self.dump_ALL_PORTS_rules,
                "data": self.all_to_ports_rules,
                "severity": 2
            },
            {
                "label": "Unused security groups",
                "description": "Security groups have no effect if there are no associated nodes.",
                "tips": "Remove security groups that are not required",
                "detect_fn": self.detect_unused_sg,
                "dump_fn": self.dump_unused_sgs,
                "data": self.unused_sgs,
                "severity": 1
            },
            {
                "label": "Nodes without any security rules",
                "description": "Nodes without security rules denied any network connections.",
                "tips": "Remove or shut down unneeded nodes",
                "detect_fn": self.detect_isolated_nodes,
                "dump_fn": self.dump_isolated_nodes,
                "data": self.lonley_nodes,
                "severity": 1
            },
            {
                "label": "Rules grant duplicate permissions",
                "description": "If more than one rule grants the same rights to the same nodes, only one rule will have an effect. Such situations can potentially lead to errors when one of the duplicate rules is changed.",
                "tips": "Rewrite the rules of the security policy. Only one rule may allow access to any network connection point (address, port, protocol, direction).",
                "detect_fn": self.detect_duplicate,
                "dump_fn": self.dump_duplicate_rules,
                "data": self.duplicate_rules,
                "severity": 2
            },
            {
                "label": "Rules grant one-sided permissions ",
                "description": "If a rule permits connecting to a server without a corresponding rule permitting client connection (or vice versa), it only has an effect if some nodes are not available for analysis (for example, if some nodes are located outside of the cloud).",
                "tips": "Remove rules that are unnecessary or add paired rules for the connections you need.",
                "detect_fn": self.detect_asymetric,
                "dump_fn": self.dump_asymetric_rules,
                "data": self.asymetric_rules,
                "severity": 1
            },

        ]

    def make_links(self):
        # links host(subnet) -> host(subnet)
        self.make_host_host_links()
        # links host -> ALL and ALL -> host
        self.make_host_all_links()
        # links host -> EXTERNAL and EXTERNAL -> host
        self.make_host_ext_links()

    def make_host_host_links(self):
        # links host(subnet) -> host(subnet)
        r_compat = self.build_r_compat_dict(self.servers, self.clients)
        for (srv_sg, srv_r) in r_compat:
            r_list = r_compat[(srv_sg, srv_r)]
            for n in r_list:
                cln_sg = n["cln_sg"]
                cln_r = n["cln_r"]
                ports = n["ports"]
                clients = self.filter_by_addr(srv_r, self.nodes_by_sg[cln_sg])
                servers = self.filter_by_addr(cln_r, self.nodes_by_sg[srv_sg])
                if len(servers) != 0 and len(clients) != 0:
                    self.add_links(servers, clients, ports,
                                   srv_sg, srv_r, cln_sg, cln_r)
                    self.used_r.add(srv_r)
                    self.used_r.add(cln_r)
                # else:
                #    self.bad_asymetric_rules_add(servers, clients, ports,
                #                                srv_sg, srv_r, cln_sg, cln_r)

    def make_host_all_links(self):
        for sg in self.servers:
            for r in self.servers[sg]:
                if r.is_any_addr():
                    id = "ANY_ADDR_ID"
                    self.ext_things.add((id, r.naddr))
                    self.add_onesided_in_links(
                        self.nodes_by_sg[sg], r.get_port_list(), sg, r, id)
                    self.used_r.add(r)
        for sg in self.clients:
            for r in self.clients[sg]:
                if r.is_any_addr():
                    id = "ANY_ADDR_ID"
                    self.ext_things.add((id, r.naddr))
                    self.add_onesided_out_links(
                        self.nodes_by_sg[sg], r.get_port_list(), sg, r, id)
                    self.used_r.add(r)

    def make_host_ext_links(self):
        id_count = 0
        unused_rules_set = self.build_unused_rules_set(self.rules, self.used_r)
        tmp_d = {}
        for r in unused_rules_set:
            sg = self.sg_by_r(self.sgs_NG, r)
            if r.is_any_addr():
                # XXX unused 0.0.0.0/0 rule - strange
                # add it to BAD list
                continue
            n = self.is_known_address(r, self.nodes)
            if len(n) != 0:
                # XXX bad link with one direction rule only
                # add it to BAD list
                continue
            nl = self.nodes_by_sg[sg]
            id = tmp_d.get(r.naddr, f"EXT_{id_count}")
            tmp_d[r.naddr] = id
            id_count += 1
            self.ext_things.add((id, r.naddr))
            if r.egress == 'True':
                self.add_onesided_in_links(
                    nl, r.get_port_list(), sg, r, id)
            else:
                self.add_onesided_out_links(
                    nl, r.get_port_list(), sg, r, id)
            self.used_r.add(r)

    def analyze_links(self):
        for i in self.analyzer_cfg:
            i["detect_fn"]()

    def detect_isolated_nodes(self):
        for n in self.nodes:
            if n.type == "IGW":
                continue
            if len(self.sglist_by_node[n]) == 0:
                self.lonley_nodes.append(n)
        self.lonley_nodes = list(set(self.lonley_nodes))

    def dump_isolated_nodes(self, c):
        d = []
        n: OneNode
        for n in self.lonley_nodes:
            t = []
            t = self.int_dump_cloud(n.cloud_id) + self.int_dump_node(n)
            d.append(t)
        return self.build_dump_res(d, c)

    def build_dump_res(self, d, c):
        severity = c["severity"]
        (caption, data) = self.transfer_av(d)
        if len(data) == 0:
            severity = 0

        res = {"label": c["label"], "description": c["description"], "severity": severity,
               "caption": caption, "data": data, "tips": c["tips"]}
        return res

    def detect_to_ANY_ports(self):
        # ANY ports and Addrs
        # nodes_by_sg = self.build_nodes_by_sg_dict(self, nodes, subnets, sgs_NG)
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress != "True":
                continue
            if r.proto != "ICMP" and r.is_all_ports():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_to_ALL_PORTS_rules(r, nlist)

    def detect_from_ANY_ports(self):
        # ANY ports and Addrs
        # nodes_by_sg = self.build_nodes_by_sg_dict(self, nodes, subnets, sgs_NG)
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress == "True":
                continue
            if r.proto != "ICMP" and r.is_all_ports():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_from_ALL_PORTS_rules(r, nlist)

    def detect_to_ANY_IPs(self):
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress != "True":
                continue
            if r.is_any_addr():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_to_ALL_IP_rules(r, nlist)

    def detect_from_ANY_IPs(self):
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress == "True":
                continue
            if r.is_any_addr():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_from_ALL_IP_rules(r, nlist)

    def detect_duplicate(self):
        # duplicate rules
        duplicates = {}
        for r1 in self.rules:
            if r1.action != 'allow':
                continue
            if r1.is_all_ports():
                continue
            for r2 in self.rules:
                if r2.action != 'allow':
                    continue
                if r1.rule_id == r2.rule_id:
                    continue
                if r1.egress != r2.egress:
                    continue
                if r1.is_any_addr() or r2.is_any_addr():
                    continue
                plist1 = r1.get_port_list()
                plist2 = r2.get_port_list()
                if r1.is_all_ports():
                    # ports = set(plist2)
                    continue
                else:
                    if r2.is_all_ports():
                        ports = set(plist1)
                    else:
                        ports = set(plist1).intersection(set(plist2))
                if len(ports) == 0:
                    continue
                a1 = ip_network(r1.naddr)
                a2 = ip_network(r2.naddr)
                if r1.cloud_id == r2.cloud_id and a1.overlaps(a2):
                    sg1 = self.sg_by_r(self.sgs_NG, r1)
                    sg2 = self.sg_by_r(self.sgs_NG, r2)
                    nset1 = set(self.nodes_by_sg[sg1])
                    nset2 = set(self.nodes_by_sg[sg2])
                    ncommon = nset1.intersection(nset2)
                    if len(ncommon) > 0:
                        if duplicates.get((r1, r2), None) == None and duplicates.get((r2, r1), None) == None:
                            duplicates[(r1, r2)] = (list(ports), list(ncommon))
        for (r1, r2) in duplicates:
            # sglist = set()
            # for t in duplicates[r]:
            #     sglist.add(self.sg_by_r(t))
            (p, n) = duplicates[(r1, r2)]
            self.add_duplicate_rules([r1, r2], p, n)

    def detect_asymetric(self):
        # one-sided rules
        for r1 in self.rules:
            if r1.is_all_ports():
                continue
            if r1.is_any_addr():
                continue
            sg1 = self.sg_by_r(self.sgs_NG, r1)
            r1nodes = self.nodes_by_sg[sg1]
            nlist1 = self.is_known_address(r1, self.nodes)
            if len(nlist1) == 0:
                # external thing
                continue
            sglist2 = []
            for n in nlist1:
                sglist2 = sglist2 + self.sglist_by_node[n]
            rlist2 = []
            for sg in sglist2:
                rlist2 = rlist2 + sg.rules
            plist1 = r1.get_port_list()
            remain_plist1 = plist1
            for r2 in rlist2:
                if r2.egress == r1.egress:
                    continue
                plist2 = r2.get_port_list()
                common_ports = set(plist2).intersection(remain_plist1)
                if not r2.is_all_ports() and len(common_ports) == 0:
                    continue
                nlist2 = self.is_known_address(r2, self.nodes)
                common_nodes = set(r1nodes).intersection(set(nlist2))
                if len(common_nodes) == 0:
                    continue
                remain_plist1 = list(
                    set(remain_plist1).difference(common_ports))
            if len(remain_plist1) == 0:
                continue
            reason = f"Assymetrical rule for ports {remain_plist1}"
            self.add_asymetric_rules(r1, remain_plist1, r1nodes)

    def detect_unused_sg(self):
        for sg in self.sgs_NG:
            nlist = self.nodes_by_sg[sg]
            if len(nlist) == 0:
                self.add_unused_sgs(sg)

    def add_unused_sgs(self, sg: RuleGroupNG):
        self.unused_sgs.append(sg)

    def dump_unused_sgs(self, c):
        d = []
        sg: RuleGroupNG
        for sg in self.unused_sgs:
            t = []
            t = t + self.int_dump_cloud(sg.cloud_id) + \
                [{"attr": "Security Group", "val": [f"{sg.name}"]}]
            d.append(t)
        return self.build_dump_res(d, c)

    def add_from_ALL_PORTS_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        for (r1, n1) in self.all_from_ports_rules:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        self.all_from_ports_rules.append(i)

    def add_to_ALL_PORTS_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        for (r1, n1) in self.all_to_ports_rules:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        self.all_to_ports_rules.append(i)

    def dump_ALL_PORTS_rules(self, c):
        d = []
        caption = []
        r: Rule
        for (r, nlist) in c["data"]:
            t = []
            t = t + self.int_dump_cloud(r.cloud_id) + self.int_dump_sg_by_r(
                r) + self.int_dump_rule_without_ports(r) + self.int_dump_afected_nodes(nlist)
            d.append(t)
        return self.build_dump_res(d, c)

    def transfer_av(self, avs: list):
        caption = []
        data = []
        if len(avs) == 0:
            return (caption, data)
        for t in avs[0]:
            caption.append(t["attr"])
        for l in avs:
            line = []
            for av in l:
                val = av["val"]
                if not type(val) is list:
                    val = [val]
                vl = []
                for s in val:
                    if len(s) > 16:
                        label = s.split("/")[-1]
                        hint = s
                        s = {"name": label, "hint": hint}
                    vl.append(s)
                line.append(vl)
            data.append(line)
        return (caption, data)

    def add_from_ALL_IP_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        for (r1, n1) in self.all_from_ip_rules:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        self.all_from_ip_rules.append(i)

    def add_to_ALL_IP_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        for (r1, n1) in self.all_to_ip_rules:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        self.all_to_ip_rules.append(i)

    def dump_ALL_IP_rules(self, c):
        d = []
        r: Rule
        for (r, nlist) in c["data"]:
            t = []
            t = t + self.int_dump_cloud(r.cloud_id) + self.int_dump_sg_by_r(
                r) + self.int_dump_rule_without_addr(r) + self.int_dump_afected_nodes(nlist)
            d.append(t)
        return self.build_dump_res(d, c)

    def int_dump_afected_nodes(self, nlist: list[OneNode]):
        t = []
        n: OneNode
        for n in nlist:
            t.append(f"{n.name}")
        i = {"attr": "Affected Nodes", "val": t}
        return [i]

    def int_dump_node(self, n: OneNode):
        # [{"attr": "Node Id", "val": n.name}]
        return [{"attr": "Node Id", "val": n.name}]

    def int_dump_rulelist(self, rlist: list[Rule]):
        t = []
        r: Rule
        for r in rlist:
            t.append(
                f"id: {r.rule_id}, addr: {r.naddr}, proto: {r.proto}, ports: {r.ports}, egress: {r.egress}")
        i = {"attr": "Rules", "val": t}
        return [i]

    def int_dump_portlist(self, portlist: list[int]):
        i = {"attr": "Ports", "val": portlist}
        return [i]

    def int_dump_sg_by_r(self, r: Rule):
        sg = self.sg_by_r(self.sgs_NG, r)
        i = {"attr": "Security Group", "val": [f"{sg.name}"]}
        return [i]

    def int_dump_cloud(self, cloud_id):
        cl: Cloud
        cl = self.get_cloud_by_id(cloud_id)
        i1 = {"attr": "Cloud type", "val": [f"{cl.cloud_type}"]}
        i2 = {"attr": "Cloud name", "val": [f"{cl.name}"]}
        return [i1, i2]

    def int_dump_rule(self, r: Rule):
        data = []
        i = {"attr": "Rule",
             "val": [f"id: {r.rule_id}", f"proto: {r.proto}", f"remote addr: {r.naddr}", f"ports: {r.ports}", f"egress: {r.egress}"]}
        data.append(i)
        return data

    def int_dump_rule_without_addr(self, r: Rule):
        i = {"attr": "Rule",
             "val": [f"id: {r.rule_id}", f"proto: {r.proto}", f"ports: {r.ports}", f"egress: {r.egress}"]}
        return [i]

    def int_dump_rule_without_ports(self, r: Rule):
        i = {"attr": "Rule",
             "val": [f"id: {r.rule_id}", f"addr: {r.naddr}", f"proto: {r.proto}", f"egress: {r.egress}"]}
        return [i]

    def add_duplicate_rules(self, rlist: list[Rule], ports: list[int], affected_nodes: list[OneNode]):
        i = (rlist, ports, affected_nodes)
        self.duplicate_rules.append(i)

    def dump_duplicate_rules(self, c):
        d = []
        for (rlist, ports, affected_nodes) in self.duplicate_rules:
            t = []
            t = t + self.int_dump_cloud(rlist[0].cloud_id) + self.int_dump_rulelist(
                rlist) + self.int_dump_portlist(ports) + self.int_dump_afected_nodes(affected_nodes)
            d.append(t)
        return self.build_dump_res(d, c)

    def add_asymetric_rules(self, r: Rule, ports: list[int], affected_nodes: list[OneNode]):
        i = (r, ports, affected_nodes)
        self.asymetric_rules.append(i)

    def dump_asymetric_rules(self, c):
        d = []
        for (r, ports, affected_nodes) in self.asymetric_rules:
            t = []
            t = t + self.int_dump_cloud(r.cloud_id) + self.int_dump_sg_by_r(
                r) + self.int_dump_rule(r) + self.int_dump_portlist(ports) + self.int_dump_afected_nodes(affected_nodes)
            d.append(t)
        return self.build_dump_res(d, c)

    def dump_analize_rezults(self):
        res = []
        for i in self.analyzer_cfg:
            t = i["dump_fn"](i)
            res.append(t)

        return res

    def get_max_severity(self):
        max_severity = 0
        for i in self.analyzer_cfg:
            if len(i["data"]) == 0:
                continue
            if i["severity"] > max_severity:
                max_severity = i["severity"]
        return max_severity

    def get_cloud_by_id(self, cloud_id):
        res = None
        for cl in self.clouds:
            if cl.id == cloud_id:
                res = cl
                break
        return res

    def build_sglist_by_node_dict(self):
        res = {}
        for n in self.nodes:
            res[n] = []
            subnet = self.get_subnet_by_node(n)
            for sg in self.sgs_NG:
                if self.is_node_in_sg(n, sg):
                    res[n].append(sg)
                    continue
                if subnet != None and self.is_subnet_in_sg(subnet, sg):
                    res[n].append(sg)
        return res

    def get_subnet_by_node(self, n: OneNode):
        for s in self.subnets:
            if n.cloud_id == s.cloud_id and n.vpc_id == s.vpc_id and n.subnet_id == s.name:
                return s
        return None

    def build_unused_rules_set(self, rules: list[Rule], used_rules):
        s1 = set()
        s2 = set()
        for r in rules:
            s1.add(r.id)
        for r in used_rules:
            s2.add(r.id)
        s3 = s1.difference(s2)
        res = set()
        for r in rules:
            if r.id in s3:
                res.add(r)
        return res

    def is_known_address(self, r: Rule, nodes: list[OneNode]):
        a1 = ip_network(r.naddr)
        nl = []
        for n in nodes:
            if r.cloud_id != n.cloud_id:
                continue
            if n.privip != None and n.privip != '':
                a2 = ip_network(n.privip)
                if a1.overlaps(a2):
                    nl.append(n)
            if n.pubip != None and n.pubip != '':
                a2 = ip_network(n.pubip)
                if a1.overlaps(a2):
                    nl.append(n)
        return nl

    def sg_by_r(self, sgs_NG: list[RuleGroupNG], r: Rule):
        res = None
        for sg in sgs_NG:
            if sg.name == r.group_id and sg.cloud_id == r.cloud_id:
                res = sg
                break
        return res

    def build_r_compat_dict(self, servers, clients):
        r_compat = {}
        for sg in servers:
            for r in servers[sg]:
                r_compat[(sg, r)] = self.find_clients_r_for_server_r(
                    r, clients)
        return r_compat

    def build_servers_clients_rule_dict(self, sgs_NG: list[RuleGroupNG], rules: list[Rule]):
        servers = {}
        clients = {}
        sg: RuleGroupNG
        for sg in sgs_NG:
            servers[sg] = []
            clients[sg] = []
            for r in sg.rules:
                if r.action != "allow":
                    continue
                if r.egress == "True":
                    servers[sg].append(r)
                else:
                    clients[sg].append(r)
        return (servers, clients)

    def build_nodes_by_sg_dict(self):
        nodes_by_sg = {}
        for sg in self.sgs_NG:
            nodes_by_sg[sg] = []
            for node in self.nodes:
                if self.is_node_in_sg(node, sg):
                    nodes_by_sg[sg].append(node)
            for subnet in self.subnets:
                if self.is_subnet_in_sg(subnet, sg):
                    nodes_by_sg[sg] = nodes_by_sg[sg] + \
                        self.get_subnet_nodelist(subnet, self.nodes)
        return nodes_by_sg

    def is_node_in_sg(self, node: OneNode, sg: RuleGroupNG):
        if node.if_id == '' or node.if_id == None:
            return False
        return node.if_id in sg.if_ids

    def is_subnet_in_sg(self, subnet: Subnet, sg: RuleGroupNG):
        return subnet.name in sg.subnet_ids

    def find_clients_r_for_server_r(self, srv_r: Rule, clients):
        res = []
        for sg in clients:
            r_list = clients[sg]
            for r in r_list:
                id1 = r.cloud_id
                id2 = srv_r.cloud_id
                if id1 != id2:
                    continue
                if r.proto != srv_r.proto:
                    continue
                if srv_r.proto == "ICMP":
                    res.append({"cln_sg": sg, "cln_r": r, "ports": [0]})
                else:
                    ports = self.get_intersection_ports(srv_r, r)
                    if len(ports) != 0:
                        res.append({"cln_sg": sg, "cln_r": r, "ports": ports})
        return res

    def get_intersection_ports(self, r1: Rule, r2: Rule):
        # special cases
        if r1.is_all_ports() and r2.is_all_ports():
            return [0]
        r1_list = r1.get_port_list()
        r2_list = r2.get_port_list()
        if r1.is_all_ports():
            return r2_list
        if r2.is_all_ports():
            return r1_list
        res = list(set(r1_list).intersection(set(r2_list)))
        return res

    def get_subnet_nodelist(self, subnet: Subnet, nodes: list[OneNode]):
        return [n for n in nodes if n.subnet_id == subnet.name]

    def filter_by_addr(self, r: Rule, nl: list[OneNode]):
        # special cases
        if r.is_any_addr():
            return []
            # res = []
            # for n in nl:
            #    if n.cloud_id == r.cloud_id:
            #        res.append(n)
            # return res
        if r.naddr == "/32":
            return nl
            # return []
        r_addr = ip_network(r.naddr)
        res = []
        for n in nl:
            if n.privip != "" and n.privip != "None":
                if ip_network(n.privip).overlaps(r_addr):
                    res.append(n)
                    continue
            if n.pubip != "" and n.pubip != "None" and n.pubip != None:
                if ip_network(n.pubip).overlaps(r_addr):
                    res.append(n)
        return res

    def add_links(self, srv: list[OneNode], cln: list[OneNode], ports: list[int], srv_sg: RuleGroupNG, srv_r: Rule, cln_sg: RuleGroupNG, cln_r: Rule):
        for sn in srv:
            for cn in cln:
                key = (sn, cn)
                if self.links_info.get(key, None) == None:
                    self.links_info[key] = []
                self.links_info[key].append((srv_sg, srv_r, cln_sg, cln_r))
                self.links.add(key)

    def add_onesided_out_links(self, cln: list[OneNode], ports: list[int], sglist: list[RuleGroupNG], r: Rule, second_id):
        for cn in cln:
            key = (None, cn, second_id)
            if self.onesided_links_info.get(key, None) == None:
                self.onesided_links_info[key] = []
            self.onesided_links_info[key].append(r)
            self.onesided_links.add(key)

    def add_onesided_in_links(self, srv: list[OneNode], ports: list[int], sglist: list[RuleGroupNG], r: Rule, second_id):
        for sn in srv:
            key = (sn, None, second_id)
            if self.onesided_links_info.get(key, None) == None:
                self.onesided_links_info[key] = []
            self.onesided_links_info[key].append(r)
            self.onesided_links.add(key)

    def get_links(self):
        return self.links

    def dump_links(self, idlist_by_node: dict):
        res = []
        i = 0
        # two sided
        for (srv, cln) in self.links:
            for sn_id in idlist_by_node[srv]:
                for cn_id in idlist_by_node[cln]:
                    (tooltip_srv, tooltip_cln) = self.make_tooltip(srv, cln)
                    res.append({"id": i, "dst": sn_id, "src": cn_id,
                               "dstTooltip": tooltip_srv, "srcTooltip": tooltip_cln})
                    i += 1
        # one sided
        for (srv, cln, second_id) in self.onesided_links:
            if srv != None:
                for sn_id in idlist_by_node[srv]:
                    tooltip = self.make_onesided_tooltip(srv, None, second_id)
                    res.append({"id": i, "dst": sn_id, "src": second_id,
                               "dstTooltip": tooltip, "srcTooltip": ""})
                    i += 1
            if cln != None:
                for cn_id in idlist_by_node[cln]:
                    tooltip = self.make_onesided_tooltip(None, cln, second_id)
                    res.append({"id": i, "dst": second_id, "src": cn_id,
                               "dstTooltip": "", "srcTooltip": tooltip})
                    i += 1
        return res

    def make_tooltip(self, srv, cln):
        key = (srv, cln)
        l = self.links_info[key]
        srv_tt = ""
        cln_tt = ""
        srv_sg: RuleGroupNG
        cln_sg: RuleGroupNG
        srv_r: Rule
        cln_r: Rule
        cln_tmp = set()
        srv_tmp = set()
        for (srv_sg, srv_r, cln_sg, cln_r) in l:
            if srv_r.proto == "ICMP":
                sp = srv_r.ports
                cp = cln_r.ports
            else:
                sp = f"Ports: {srv_r.ports}"
                cp = f"Ports: {cln_r.ports}"
            srv_tmp.add(
                f"Group: {srv_sg.name}, Proto: {srv_r.proto}, Addr: {srv_r.naddr}, {sp}\n")
            cln_tmp.add(
                f"Group: {cln_sg.name}, Proto: {cln_r.proto}, Addr: {cln_r.naddr}, {cp}\n")
        for s in srv_tmp:
            srv_tt = srv_tt + s
        for s in cln_tmp:
            cln_tt = cln_tt + s

        return (srv_tt, cln_tt)

    def make_onesided_tooltip(self, srv, cln, second_id):
        key = (srv, cln, second_id)
        l = self.onesided_links_info[key]
        tt = ""
        sg: RuleGroupNG
        r: Rule
        tmp = set()
        for r in l:
            if r.proto == "ICMP":
                p = r.ports
            else:
                p = f"Ports:{r.ports}"
            tmp.add(f"Proto: {r.proto}, {p}\n")
        for s in tmp:
            tt = tt + s
        return tt
