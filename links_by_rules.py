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
        self.all_ports_rules = []
        self.all_ip_rules = []
        self.duplicate_rules = []
        self.asymetruc_rules = []
        self.alone_nodes = []
        self.alone_sg = []
        (self.servers, self.clients) = self.build_servers_clients_rule_dict(
            self.sgs_NG, rules)
        self.nodes_by_sg = self.build_nodes_by_sg_dict()
        self.sglist_by_node = self.build_sglist_by_node_dict()

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
        # find ANY PORTS and ANY ADDRs links
        self.detect_ANY()
        self.detect_duplicate()
        self.detect_asymetric()
        # XXX detect isolated nodes
        # XXX detect security groups without nodes

    def detect_ANY(self):
        # ANY ports and Addrs
        # nodes_by_sg = self.build_nodes_by_sg_dict(self, nodes, subnets, sgs_NG)
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.proto != "ICMP" and r.is_all_ports():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_ALL_PORTS_rules(r, nlist)
            if r.is_any_addr():
                sg = self.sg_by_r(self.sgs_NG, r)
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_ALL_IP_rules(r, nlist)

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
                if r1.id == r2.id:
                    continue
                if r1.egress != r2.egress:
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
                        if duplicates.get(r1, None) == None:
                            duplicates[r1] = set([r1])
                        duplicates[r1].add(r2)
        keys_for_remove = set()
        for r in duplicates:
            for t in duplicates:
                if r == t:
                    continue
                if duplicates[r] == duplicates[t]:
                    keys_for_remove.add(t)
        for key in keys_for_remove:
            del duplicates[key]
        for r in duplicates:
            # sglist = set()
            # for t in duplicates[r]:
            #     sglist.add(self.sg_by_r(t))
            self.add_duplicate_rules(duplicates[r], ports, ncommon)

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

    def add_ALL_PORTS_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        self.all_ports_rules.append(i)

    def dump_ALL_PORTS_rules(self):
        data = []
        r: Rule
        for (r, nlist) in self.all_ports_rules:
            data = data + self.int_dump_cloud_by_r(r)
            data = data + self.int_dump_sg_by_r(r)
            data = data + self.int_dump_rule(r)
            data = data + self.int_dump_afected_nodes(nlist)
        res = {"label": "Rules to/from ANY ports", "data": data}
        return res

    def add_ALL_IP_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        self.all_ip_rules.append(i)

    def dump_ALL_IP_rules(self):
        data = []
        r: Rule
        for (r, nlist) in self.all_ip_rules:
            data = data + self.int_dump_cloud_by_r(r)
            data = data + self.int_dump_sg_by_r(r)
            data = data + self.int_dump_rule(r)
            data = data + self.int_dump_afected_nodes(nlist)
        res = {"label": "Rules to/from ANY IPs", "data": data}
        return res

    def int_dump_afected_nodes(self, nlist: list[OneNode]):
        data = []
        t = []
        n: OneNode
        for n in nlist:
            t.append(f"{n.name}")
        i = {"attr": "Affected Nodes", "val": t}
        data.append(i)
        return data

    def int_dump_sg_by_r(self, r: Rule):
        data = []
        sg = self.sg_by_r(self.sgs_NG, r)
        i = {"attr": "Security Group", "val": [f"{sg.name}"]}
        data.append(i)
        return data

    def int_dump_cloud_by_r(self, r: Rule):
        data = []
        cl: Cloud
        cl = self.get_cloud_by_id(r.cloud_id)
        i = {"attr": "Cloud type", "val": [f"{cl.cloud_type}"]}
        data.append(i)
        i = {"attr": "Cloud name", "val": [f"{cl.name}"]}
        data.append(i)
        return data

    def int_dump_rule(self, r: Rule):
        data = []
        i = {"attr": "Rule",
             "val": [f"id: {r.id}, ports: {r.ports}, egress: {r.egress} proto: {r.proto}"]}
        data.append(i)
        return data

    def add_duplicate_rules(self, rlist: list[Rule], ports: list[int], affected_nodes: list[OneNode]):
        i = (rlist, ports, affected_nodes)
        self.duplicate_rules.append(i)

    def add_asymetric_rules(self, r: Rule, ports: list[int], affected_nodes: list[OneNode]):
        i = (r, ports, affected_nodes)
        self.asymetruc_rules.append(i)

    def add_alone_node(self, affected_node: OneNode):
        self.alone_nodes.append(affected_node)

    def add_alone_sg(self, affected_sg: RuleGroupNG):
        self.alone_sg.append(affected_sg)

    def dump_analize_rezults(self):
        res = []
        # res = [{"label": label, "size": size,  "data": data}]
        # data = [{"attr": attr, "type": type, "value": value}]
        t = self.dump_ALL_PORTS_rules()
        res.append(t)
        t = self.dump_ALL_IP_rules()
        res.append(t)

        return res

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
