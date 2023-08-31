from subnet import Subnet
from vm import OneNode
from rule_group import RuleGroup
from rule import Rule
from classifiers_list import classifier, vminfo
from ipaddress import ip_network


class links_by_rules:
    def __init__(self, nodes: list[OneNode], subnets: list[Subnet], sgs: list[RuleGroup], rules: list[Rule]):
        self.links = set()
        self.links_info = {}
        self.servers = {}
        self.clients = {}
        for sg in sgs:
            self.servers[sg] = []
            self.clients[sg] = []
            for r in rules:
                if r.group_id != sg.name:
                    continue
                if r.action != "allow":
                    continue
                if r.egress == "True":
                    self.servers[sg].append(r)
                else:
                    self.clients[sg].append(r)
        r_compat = {}
        for sg in self.servers:
            for r in self.servers[sg]:
                r_compat[(sg, r)] = self.find_clients_r_for_server_r(r)
        nodes_by_sg = {}
        for sg in sgs:
            nodes_by_sg[sg] = []
            for node in nodes:
                if self.is_node_in_sg(node, sg):
                    nodes_by_sg[sg].append(node)
        for (srv_sg, srv_r) in r_compat:
            r_list = r_compat[(srv_sg, srv_r)]
            for n in r_list:
                cln_sg = n["cln_sg"]
                cln_r = n["cln_r"]
                ports = n["ports"]
                clients = self.filter_by_addr(srv_r, nodes_by_sg[cln_sg])
                servers = self.filter_by_addr(cln_r, nodes_by_sg[srv_sg])
                if len(servers) != 0 and len(clients) != 0:
                    self.add_links(servers, clients, ports,
                                   srv_sg, srv_r, cln_sg, cln_r)

    def is_node_in_sg(self, node: OneNode, sg: RuleGroup):
        return node.if_id == sg.if_id

    def find_clients_r_for_server_r(self, srv_r: Rule):
        res = []
        for sg in self.clients:
            r_list = self.clients[sg]
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

    def filter_by_addr(self, r: Rule, nl: list[OneNode]):
        # special cases
        if r.naddr == "0.0.0.0/0":
            # XXX return nl
            return []
        if r.naddr == "/32":
            return nl
            # return []
        r_addr = ip_network(r.naddr)
        res = []
        for n in nl:
            if n.privip == "" or n.privip == "None":
                # XXX may be we need check node subnet addr here?
                continue
            if ip_network(n.privip).overlaps(r_addr):
                res.append(n)
        return res

    def add_links(self, srv: list[OneNode], cln: list[OneNode], ports: list[int], srv_sg: RuleGroup, srv_r: Rule, cln_sg: RuleGroup, cln_r: Rule):
        for sn in srv:
            for cn in cln:
                key = (sn, cn)
                if self.links_info.get(key, None) == None:
                    self.links_info[key] = []
                self.links_info[key].append((srv_sg, srv_r, cln_sg, cln_r))
                self.links.add(key)

    def get_links(self):
        return self.links

    def dump_links(self, idlist_by_node: dict):
        res = []
        i = 0
        t = set()
        for (srv, cln) in self.links:
            for sn_id in idlist_by_node[srv]:
                for cn_id in idlist_by_node[cln]:
                    (tooltip_srv, tooltip_cln) = self.make_tooltip(srv, cln)
                    res.append({"id": i, "dst": sn_id, "src": cn_id,
                               "dstTooltip": tooltip_srv, "srcTooltip": tooltip_cln})
                    i += 1
        return res

    def make_tooltip(self, srv, cln):
        key = (srv, cln)
        l = self.links_info[key]
        srv_tt = ""
        cln_tt = ""
        srv_sg: RuleGroup
        cln_sg: RuleGroup
        srv_r: Rule
        cln_r: Rule
        for (srv_sg, srv_r, cln_sg, cln_r) in l:
            srv_tt = srv_tt + \
                f"Group: {srv_sg.id}, Proto: {srv_r.proto}, Addr: {srv_r.naddr}, Ports: {srv_r.ports}\n"
            cln_tt = cln_tt + \
                f"Group: {cln_sg.id}, Proto: {cln_r.proto}, Addr: {cln_r.naddr}, Ports: {cln_r.ports}\n"

        return (srv_tt, cln_tt)
