from ipaddress import ip_network, ip_address

from .ctx import CTX
from .subnet import Subnet
from .vm import OneNode
from .rule_group import RuleGroup, RuleGroupNG, convert_RuleGroup_to_NG, convert_RuleGroup_to_sgNG, convert_RuleGroup_to_naclNG
from .rule import Rule
from .classifiers_list import classifier, vminfo
from .cloud import Cloud
from .vpc import VPC

SG = "sg"
ACL = "acl"


class links_by_rules(CTX):
    def __init__(self, clouds: list[Cloud], nodes: list[OneNode], subnets: list[Subnet], sgs1: list[RuleGroup], rules: list[Rule]):
        self.sgs_NG = convert_RuleGroup_to_sgNG(sgs1, rules)
        self.nacls_NG = convert_RuleGroup_to_naclNG(sgs1, rules)
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

        # issues
        self.all_from_ports_rules = []
        self.all_to_ports_rules = []
        self.all_from_ip_rules_sg = []
        self.all_to_ip_rules_sg = []
        self.all_from_ip_rules_acl = []
        self.all_to_ip_rules_acl = []
        self.duplicate_rules = []
        self.asymetric_rules = []
        self.lonley_nodes = []
        self.unused_sgs = []
        self.pubIP_VMs = []
        self.port_tcp80 = []
        self.port_tcp20 = []
        self.port_tcp21 = []
        self.port_tcp23 = []
        self.port_tcp79 = []

        (self.servers, self.clients) = self.build_servers_clients_rule_dict(
            self.sgs_NG, rules)
        self.nodes_by_sg = self.build_nodes_by_sg_dict()
        self.sglist_by_node = self.build_sglist_by_node_dict()

        self.analyzer_cfg = [
            {
                "label": "Ingress security rules with ANY IPs",
                "description": "Except for public resources, unrestricted connection from ANY (0.0.0.0) address is considered bad practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_from_ANY_IPs_sg,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_from_ip_rules_sg,
                "datatype": "rules",
                "severity": 3
            },
            {
                "label": "Egress security rules with ANY IPs",
                "description": "Unrestricted connection to ANY (0.0.0.0) address in general is not a recommended practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_to_ANY_IPs_sg,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_to_ip_rules_sg,
                "datatype": "rules",
                "severity": 2
            },
            {
                "label": "Ingress subdirectory NACLs with ANY IPs",
                "description": "Except for public resources, unrestricted connection from ANY (0.0.0.0) address is considered bad practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_from_ANY_IPs_acl,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_from_ip_rules_acl,
                "datatype": "rules",
                "severity": 2
            },
            {
                "label": "Egress subdirectory NACLs with ANY IPs",
                "description": "Unrestricted connection to ANY (0.0.0.0) address in general is not a recommended practice.",
                "tips": "Restrict the range of addresses in the security rules, if possible",
                "detect_fn": self.detect_to_ANY_IPs_acl,
                "dump_fn": self.dump_ALL_IP_rules,
                "data": self.all_to_ip_rules_acl,
                "datatype": "rules",
                "severity": 1
            },
            {
                "label": "Rules from ANY Ports",
                "description": "Granting permission to open connections from any port in general is not a recommended practice.",
                "tips": "If possible, limit the range of ports in the security rules.",
                "detect_fn": self.detect_from_ANY_ports,
                "dump_fn": self.dump_PORTS_rules,
                "data": self.all_from_ports_rules,
                "datatype": "rules",
                "severity": 1
            },
            {
                "label": "Rules to ANY Ports",
                "description": "Except for special cases where the node acts as a NAT or Gateway, opening all ports on the node is not a recommended practice.",
                "tips": "If possible, limit the range of ports in the security rules.",
                "detect_fn": self.detect_to_ANY_ports,
                "dump_fn": self.dump_PORTS_rules,
                "data": self.all_to_ports_rules,
                "datatype": "rules",
                "severity": 2
            },
            {
                "label": "Unused security groups",
                "description": "Security groups have no effect if there are no associated nodes.",
                "tips": "Remove security groups that are not required",
                "detect_fn": self.detect_unused_sg,
                "dump_fn": self.dump_unused_sgs,
                "data": self.unused_sgs,
                "datatype": "securitygroups",
                "severity": 1
            },
            {
                "label": "Nodes without any security rules",
                "description": "Nodes without security rules denied any network connections.",
                "tips": "Remove or shut down unneeded nodes",
                "detect_fn": self.detect_isolated_nodes,
                "dump_fn": self.dump_nodes,
                "data": self.lonley_nodes,
                "datatype": "nodes",
                "severity": 1
            },
            {
                "label": "Rules grant duplicate permissions",
                "description": "If more than one rule grants the same rights to the same nodes, only one rule will have an effect. Such situations can potentially lead to errors when one of the duplicate rules is changed.",
                "tips": "Rewrite the rules of the security policy. Only one rule may allow access to any network connection point (address, port, protocol, direction).",
                "detect_fn": self.detect_duplicate,
                "dump_fn": self.dump_duplicate_rules,
                "data": self.duplicate_rules,
                "datatype": "rulepairs",
                "severity": 2
            },
            {
                "label": "Rules grant one-sided permissions",
                "description": "If a rule permits connecting to a server without a corresponding rule permitting client connection (or vice versa), it only has an effect if some nodes are not available for analysis (for example, if some nodes are located outside of the cloud).",
                "tips": "Remove rules that are unnecessary or add paired rules for the connections you need.",
                "detect_fn": self.detect_asymetric,
                "dump_fn": self.dump_asymetric_rules,
                "data": self.asymetric_rules,
                "datatype": "rules",
                "severity": 1
            },
            {
                "label": "VM nodes with public IP",
                "description": "Connecting VM directly to Internet increases the attack surface",
                "tips": "Connect VM through NAT/LB infrastructure",
                "detect_fn": self.detect_VM_pubIP,
                "dump_fn": self.dump_nodes,
                "data": self.pubIP_VMs,
                "datatype": "nodes",
                "severity": 1
            },
            {
                "label": "Using unsafe protocols: HTTP",
                "description": "Granting permission to use unsafe HTTP protocol.",
                "tips": "If possible, change HTTP protocol to more secure HTTPS.",
                "detect_fn": self.detect_tcp80,
                "dump_fn": self.dump_PORTS_rules,
                "datatype": "rules",
                "data": self.port_tcp80,
                "severity": 3
            },
            {
                "label": "Using unsafe protocols: FTP (command)",
                "description": "Granting permission to use unsafe FTP protocol.",
                "tips": "If possible, change FTP protocol to more secure FTP over SSL/TLS.",
                "detect_fn": self.detect_tcp21,
                "dump_fn": self.dump_PORTS_rules,
                "datatype": "rules",
                "data": self.port_tcp21,
                "severity": 1
            },
            {
                "label": "Using unsafe protocols: FTP (data)",
                "description": "Granting permission to use unsafe FTP protocol.",
                "tips": "If possible, change FTP protocol to more secure FTP over SSL/TLS.",
                "detect_fn": self.detect_tcp20,
                "dump_fn": self.dump_PORTS_rules,
                "datatype": "rules",
                "data": self.port_tcp20,
                "severity": 1
            },
            {
                "label": "Using unsafe protocols: Telnet (23/TCP)",
                "description": "Granting permission to use unsafe Telnet protocol.",
                "tips": "If possible, change Telnet protocol to more secure SSH.",
                "detect_fn": self.detect_tcp23,
                "dump_fn": self.dump_PORTS_rules,
                "datatype": "rules",
                "data": self.port_tcp23,
                "severity": 1
            },
            {
                "label": "Using unsafe protocols: Finger (79/TCP)",
                "description": "Granting permission to use unsafe Finger protocol.",
                "tips": "If possible, do not use finger protocol",
                "detect_fn": self.detect_tcp79,
                "dump_fn": self.dump_PORTS_rules,
                "datatype": "rules",
                "data": self.port_tcp79,
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
        # NACL for Azure
        self.apply_NACL()

    def apply_NACL(self):
        # two-sided links
        for (sn, cn) in self.links:
            link_key = (sn, cn)
            if not self.is_aws(sn.cloud_id) and not self.is_aws(cn.cloud_id):
                continue
            linfo_list = self.links_info[link_key]
            for (srv_sg, srv_r, cln_sg, cln_r) in linfo_list:
                link_info = (srv_sg, srv_r, cln_sg, cln_r)
                if self.is_aws(sn.cloud_id):
                    nacl = self.get_nacl(sn)
                    if nacl != None and not self.is_srv_nacl_compatible(nacl, cn.privip, srv_r):
                        self.delete_link(link_key, link_info)
                if self.is_aws(cn.cloud_id):
                    nacl = self.get_nacl(cn)
                    if nacl != None and not self.is_cln_nacl_compatible(nacl, sn.privip, cln_r):
                        self.delete_link(link_key, link_info)
        # one-sided links
        for (sn, cn, second_id) in self.onesided_links:
            link_key = (sn, cn, second_id)
            if sn != None and self.is_aws(sn.cloud_id):
                linfo_list = self.onesided_links_info[link_key]
                for r in linfo_list:
                    nacl = self.get_nacl(sn)
                    if nacl != None and not self.is_srv_nacl_compatible(nacl, r.naddr, r):
                        self.delete_link(link_key, r)
            if cn != None and self.is_aws(cn.cloud_id):
                linfo_list = self.onesided_links_info[link_key]
                for r in linfo_list:
                    nacl = self.get_nacl(cn)
                    if nacl != None and not self.is_cln_nacl_compatible(nacl, r.naddr, r):
                        self.delete_link(link_key, r)
        return
    
    def is_aws(self, cloud_id):
        cl:Cloud
        for cl in self.clouds:
            if cl.id == cloud_id:
                if cl.aws_key != '' and cl.aws_key != None:
                    return True
                else:
                    return False
        return False
    
    def is_srv_nacl_compatible(self, nacl, cn_ip, srv_r: Rule):
        proto = srv_r.proto
        port_list = srv_r.get_port_list()
        if not self.is_allow_in(nacl, cn_ip, proto, port_list):
            return False
        if proto == 'TCP' and not self.is_link_allow_out(nacl, cn_ip, proto, port_list):
            return False
        return True
    
    def is_cln_nacl_compatible(self, nacl, sn_ip, cln_r: Rule):
        proto = cln_r.proto
        port_list = cln_r.get_port_list()
        if not self.is_link_allow_out(nacl, sn_ip, proto, port_list):
            return False
        if proto == 'TCP' and not self.is_link_allow_in(nacl, sn_ip, proto, port_list):
            return False
        return True
    
    def is_link_allow_in(self, nacl_g : RuleGroupNG, ip, proto, port_list):
        return self.is_link_allow_by_nacl(nacl_g, False, ip, proto, port_list)
    
    def is_link_allow_out(self, nacl_g : RuleGroupNG, ip, proto, port_list):
        return self.is_link_allow_by_nacl(nacl_g, True, ip, proto, port_list)
    
    def is_link_allow_by_nacl(self, nacl_g : RuleGroupNG, direction, ip, proto, port_list):
        # find first nacl rule for ip\port_list\proto\ingress
        for nacl in nacl_g.rules:
            nacl: Rule
            if nacl.proto != proto:
                continue
            if nacl.egress != direction:
                continue           
            if not ip_network(nacl.naddr).overlaps(ip_network(ip)):
                continue
            np_list = nacl.get_port_list()
            if set(np_list).isdisjoint(set(port_list)):
                continue
            # we found it
            if nacl.action == 'DENY':
                return False
            else:
                break
        return True
        
    def delete_link(self, key, info):
        if key not in self.links:
            return
        if self.links_info.get(key, None) == None:
            self.links.remove(key)
            return
        if info in self.links_info[key]:
            self.links_info[key].remove(info)
        if self.links_info[key] == []:
            self.links.remove(key)
        return
    
    def get_nacl(self, n: OneNode):
        nacl: RuleGroupNG
        for nacl in self.nacls_NG:
            if n.subnet_id in nacl.subnet_ids:
                return nacl
        return None
    
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

    def build_dump_res(self, d, c):
        severity = c["severity"]
        (caption, data) = self.transfer_av(d)
        if len(data) == 0:
            severity = 0

        res = {"label": c["label"], "description": c["description"], "severity": severity,
               "caption": caption, "data": data, "tips": c["tips"]}
        return res

    def detect_VM_pubIP(self):
        for n in self.nodes:
            if n.type != "VM":
                continue
            if n.pubip != "" and n.pubip != None:
                self.pubIP_VMs.append(n)
        self.pubIP_VMs = list(set(self.pubIP_VMs))

    def detect_isolated_nodes(self):
        for n in self.nodes:
            if n.type == "IGW":
                continue
            if len(self.sglist_by_node[n]) == 0:
                self.lonley_nodes.append(n)
        self.lonley_nodes = list(set(self.lonley_nodes))

    def detect_tcp80(self):
        self.int_detect_ports(80, "TCP", self.port_tcp80)

    def detect_tcp20(self):
        self.int_detect_ports(20, "TCP", self.port_tcp20)

    def detect_tcp21(self):
        self.int_detect_ports(21, "TCP", self.port_tcp21)

    def detect_tcp23(self):
        self.int_detect_ports(23, "TCP", self.port_tcp23)

    def detect_tcp79(self):
        self.int_detect_ports(79, "TCP", self.port_tcp79)

    def int_detect_ports(self, port, proto, res_list):
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.proto != proto:
                continue
            if port not in r.get_port_list():
                continue
            sg = self.sg_by_r(self.sgs_NG, r)
            if sg == None:
                continue
            nlist = self.nodes_by_sg[sg]
            if len(nlist) > 0:
                self.add_PORTS_rules(res_list, r)

    def detect_to_ANY_ports(self):
        self.int_detect_ANY_ports("False", self.all_to_ports_rules)

    def detect_from_ANY_ports(self):
        self.int_detect_ANY_ports("True", self.all_from_ports_rules)

    def int_detect_ANY_ports(self, egress, res_list):
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress != egress:
                continue
            if r.proto != "ICMP" and r.is_all_ports():
                sg = self.sg_by_r(self.sgs_NG, r)
                if sg == None:
                    continue
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_PORTS_rules(res_list, r)

    def detect_from_ANY_IPs_sg(self):
        self.int_detect_ANY_IPs("False", self.sgs_NG,
                                self.all_from_ip_rules_sg)

    def detect_from_ANY_IPs_acl(self):
        self.int_detect_ANY_IPs("False", self.nacls_NG,
                                self.all_from_ip_rules_acl)

    def detect_to_ANY_IPs_sg(self):
        self.int_detect_ANY_IPs("True", self.sgs_NG, self.all_to_ip_rules_sg)

    def detect_to_ANY_IPs_acl(self):
        self.int_detect_ANY_IPs("True", self.nacls_NG,
                                self.all_to_ip_rules_acl)

    def int_detect_ANY_IPs(self, egress, sgs_list, res_list):
        for r in self.rules:
            if r.action != 'allow':
                continue
            if r.egress != egress:
                continue
            if r.is_any_addr():
                sg = self.sg_by_r(sgs_list, r)
                if sg == None:
                    continue
                nlist = self.nodes_by_sg[sg]
                if len(nlist) > 0:
                    self.add_ALL_IP_rules(res_list, r)

    def detect_duplicate(self):
        # duplicate rules
        duplicates = []
        for r1 in self.rules:
            if r1.is_all_ports():
                continue
            for r2 in self.rules:
                # if r2.is_all_ports():
                #    continue
                if r1.cloud_id != r2.cloud_id:
                    continue
                if r1.action != r2.action:
                    continue
                if r1.egress != r2.egress:
                    continue
                if r1.rule_id == r2.rule_id:
                    continue
                if r1.is_any_addr() or r2.is_any_addr():
                    continue
                plist1 = r1.get_port_list()
                if r2.is_all_ports():
                    ports = set(plist1)
                else:
                    plist2 = r2.get_port_list()
                    ports = set(plist1).intersection(set(plist2))
                if len(ports) == 0:
                    continue
                a1 = ip_network(r1.naddr)
                a2 = ip_network(r2.naddr)
                if not a1.overlaps(a2):
                    continue
                sg1 = self.sg_by_r(self.sgs_NG, r1)
                sg2 = self.sg_by_r(self.sgs_NG, r2)
                nset1 = set(self.nodes_by_sg[sg1])
                nset2 = set(self.nodes_by_sg[sg2])
                ncommon = nset1.intersection(nset2)
                if len(ncommon) == 0:
                    continue
                if (r1, r2) not in duplicates and (r2, r1) not in duplicates:
                    duplicates.append((r1, r2))
        for (r1, r2) in duplicates:
            self.add_duplicate_rules(r1, r2)

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
                if r2.is_all_ports():
                    common_ports = remain_plist1
                else:
                    plist2 = r2.get_port_list()
                    common_ports = set(plist2).intersection(remain_plist1)
                if len(common_ports) == 0:
                    continue
                nlist2 = self.is_known_address(r2, self.nodes)
                common_nodes = set(r1nodes).intersection(set(nlist2))
                if len(common_nodes) == 0:
                    continue
                remain_plist1 = list(
                    set(remain_plist1).difference(common_ports))
            if len(remain_plist1) == 0:
                continue
            self.add_asymetric_rules(r1)

    def detect_unused_sg(self):
        for sg in self.sgs_NG:
            nlist = self.nodes_by_sg[sg]
            if len(nlist) == 0:
                self.add_unused_sgs(sg)

    def dump_nodes(self, c):
        d = []
        n: OneNode
        for n in c["data"]:
            t = []
            t = self.int_dump_cloud(n.cloud_id) + self.int_dump_node(n)
            d.append(t)
        return self.build_dump_res(d, c)

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

    def add_PORTS_rules(self, rlist: list, r: Rule):
        for r1 in rlist:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        rlist.append(r)

    def dump_PORTS_rules(self, c):
        d = []
        r: Rule
        for r in c["data"]:
            t = []
            sg = self.sg_by_r(self.sgs_NG, r)
            nlist = self.nodes_by_sg[sg]
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
                    s = str(s)
                    if len(s) > 32:
                        name = s.split(":")[0]
                        if name == s:
                            name = ""
                        else:
                            name += ": "
                        label = s.split("/")[-1]
                        if name == "":
                            hint = s
                        else:
                            t = s.split(": ")
                            if len(t) == 2:
                                hint = t[1]
                            else:
                                hint = s
                        if s != label:
                            s = {"name": f"{name}{label}", "hint": hint}
                    vl.append(s)
                if len(vl) == 1:
                    vl = vl[0]
                line.append(vl)
            data.append(line)
        return (caption, data)

    def add_from_ALL_IP_rules(self, r: Rule, affected_nodes: list[OneNode]):
        i = (r, affected_nodes)
        for (r1, n1) in self.all_from_ip_rules:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        self.all_from_ip_rules.append(i)

    def add_ALL_IP_rules(self, rlist: list, r: Rule):
        for r1 in rlist:
            if r1.cloud_id == r.cloud_id and r1.rule_id == r.rule_id:
                return
        rlist.append(r)

    def dump_ALL_IP_rules(self, c):
        d = []
        r: Rule
        for r in c["data"]:
            t = []
            sg = self.sg_by_r(self.sgs_NG, r)
            if sg == None:
                sg = self.sg_by_r(self.nacls_NG, r)
            if sg == None:
                continue
            nlist = self.nodes_by_sg[sg]
            t = t + self.int_dump_cloud(r.cloud_id) + self.int_dump_sg_by_r(
                r) + self.int_dump_rule_without_addr(r) + self.int_dump_afected_nodes(nlist)
            d.append(t)
        return self.build_dump_res(d, c)

    def int_dump_afected_nodes(self, nlist: list[OneNode]):
        t = []
        n: OneNode
        for n in nlist:
            t.append(f"{n.name}")
        i = {"attr": "Affected Nodes", "val": list(set(t))}
        return [i]

    def int_dump_node(self, n: OneNode):
        # [{"attr": "Node Id", "val": n.name}]
        return [{"attr": "Node Id", "val": n.name}, {"attr": "Node name", "val": n.note}]

    def int_dump_rulelist(self, rlist: list[Rule]):
        t = []
        r: Rule
        for r in rlist:
            t.append(
                # f"rule id: {r.rule_id}, addr: {r.naddr}, proto: {r.proto}, ports: {r.ports}, egress: {r.egress}")
                f"{r.group_id}: {r.rule_id}")
        i = {"attr": "Security group: Rule", "val": t}
        return [i]

    def int_dump_portlist(self, portlist: list[int]):
        i = {"attr": "Ports", "val": portlist}
        return [i]

    def int_dump_sg_by_r(self, r: Rule):
        sg = self.sg_by_r(self.sgs_NG, r)
        if sg == None:
            sg = self.sg_by_r(self.nacls_NG, r)
        if sg == None:
            i = {"attr": "Security Group", "val": ["Unknown"]}
        else:
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

    def add_duplicate_rules(self, r1: Rule, r2: Rule):
        for (t_r1, t_r2) in self.duplicate_rules:
            if t_r1.cloud_id != r1.cloud_id:
                continue
            if t_r1.rule_id != r1.rule_id and t_r1.rule_id != r2.rule_id:
                continue
            if t_r2.rule_id != r1.rule_id and t_r2.rule_id != r2.rule_id:
                continue
            return
        self.duplicate_rules.append((r1, r2))

    def dump_duplicate_rules(self, c):
        d = []
        for (r1, r2) in self.duplicate_rules:
            plist1 = r1.get_port_list()
            if r2.is_all_ports():
                ports = set(plist1)
            else:
                plist2 = r2.get_port_list()
                ports = set(plist1).intersection(set(plist2))
            ports = list(ports)

            sg1 = self.sg_by_r(self.sgs_NG, r1)
            sg2 = self.sg_by_r(self.sgs_NG, r2)
            nset1 = set(self.nodes_by_sg[sg1])
            nset2 = set(self.nodes_by_sg[sg2])
            ncommon = nset1.intersection(nset2)
            t = []
            t = t + self.int_dump_cloud(r1.cloud_id) + self.int_dump_rulelist(
                [r1, r2]) + self.int_dump_portlist(ports) + self.int_dump_afected_nodes(ncommon)
            d.append(t)
        return self.build_dump_res(d, c)

    def add_asymetric_rules(self, r: Rule):
        for r1 in self.asymetric_rules:
            if r.cloud_id == r1.cloud_id and r.rule_id == r1.rule_id:
                return
        self.asymetric_rules.append(r)

    def dump_asymetric_rules(self, c):
        d = []
        for r in self.asymetric_rules:
            sg1 = self.sg_by_r(self.sgs_NG, r)
            nodes = self.nodes_by_sg[sg1]
            t = []
            t = t + self.int_dump_cloud(r.cloud_id) + self.int_dump_sg_by_r(
                r) + self.int_dump_rule(r) + self.int_dump_afected_nodes(nodes)
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
            ''' exclude NACL
            subnet = self.get_subnet_by_node(n)
            '''
            for sg in self.sgs_NG:
                if self.is_node_in_sg(n, sg):
                    res[n].append(sg)
                    continue
                ''' exclude NACL
                if subnet != None and self.is_subnet_in_sg(subnet, sg):
                    res[n].append(sg)
                '''
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
        for sg in sgs_NG:
            if sg.name == r.group_id and sg.cloud_id == r.cloud_id:
                return sg

        return None

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
            # exclude NACL
            if self.is_sg_acl(sg):
                continue
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
        for sg in self.nacls_NG:
            nodes_by_sg[sg] = []
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
                if r.cloud_id != srv_r.cloud_id:
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

    def same_rule_lists(self, l1: list[Rule], l2: list[Rule]):
        if len(l1) != len(l2):
            return False
        for t1 in l1:
            found = False
            for t2 in l2:
                if t1.rule_id == t2.rule_id:
                    found = True
                    break
            if not found:
                return False
        return True

    def issue_dump1(self, ext_things):
        self.vm_count = {}
        node_severity, rule_severity, sg_severity = self.issue_dump_colors(
            self.analyzer_cfg)
        u_node_severity = self.update_node_severity_by_rules(
            rule_severity, self.sgs_NG, node_severity)
        scheme = self.issue_dump_scheme(
            self.sgs_NG, ext_things, u_node_severity, sg_severity, rule_severity)
        lines = self.issue_dump_links(
            self.sgs_NG, self.rules, ext_things, rule_severity)
        return {"scheme": scheme, "lines": {"items": lines}}

    def issue_dump2(self, ext_things):
        self.vm_count = {}
        node_severity, rule_severity, sg_severity = self.issue_dump_colors(
            self.analyzer_cfg)
        u_node_severity = self.update_node_severity_by_rules(
            rule_severity, self.nacls_NG, node_severity)
        scheme = self.issue_dump_scheme(
            self.nacls_NG, ext_things, u_node_severity, sg_severity, rule_severity)
        lines = self.issue_dump_links(
            self.nacls_NG, self.rules, ext_things, rule_severity)
        return {"scheme": scheme, "lines": {"items": lines}}

    def issue_dump_colors(self, cfg_list):
        node_severity = {}
        rule_severity = {}
        sg_severity = {}
        for cfg in cfg_list:
            d = cfg['data']
            datatype = cfg['datatype']
            severity = cfg['severity']
            if datatype == 'nodes':
                for n in d:
                    id = self.get_common_id_by_vm(n)
                    cur_severity = node_severity.get(id, 0)
                    node_severity[id] = max(severity, cur_severity)
            elif datatype == 'rules':
                for r in d:
                    id = self.get_id_by_rule(r)
                    cur_severity = rule_severity.get(id, 0)
                    rule_severity[id] = max(cur_severity, severity)
            elif datatype == 'securitygroups':
                for sg in d:
                    id = self.get_id_by_sg(sg)
                    cur_severity = sg_severity.get(sg_severity[id], 0)
                    sg_severity[id] = max(cur_severity, severity)
            elif datatype == 'rulepairs':
                for (r1, r2) in d:
                    id = self.get_id_by_rule(r1)
                    cur_severity = rule_severity.get(id, 0)
                    rule_severity[id] = max(cur_severity, severity)
                    id = self.get_id_by_rule(r2)
                    cur_severity = rule_severity.get(id, 0)                    
                    rule_severity[id] = max(cur_severity, severity)
            else:
                # BUG
                None

        return node_severity, rule_severity, sg_severity

    def update_node_severity_by_rules(self, rule_severity, sg_list, node_severity):
        res = {}
        res = node_severity.copy()
        # update node severity by rules
        for r in self.rules:
            if r.is_any_addr():
                continue
            if not self.is_known_address(r, self.nodes):
                continue
            if rule_severity.get(self.get_id_by_rule(r), 0) == 0:
                continue
            sg = self.sg_by_r(sg_list, r)
            if sg == None:
                continue
            n_list = self.filter_by_addr(r, self.nodes)
            r_severity = rule_severity.get(self.get_id_by_rule(r), 0)
            for n in n_list:
                cur_severity = res.get(
                    self.get_common_id_by_vm(n), 0)
                res[self.get_common_id_by_vm(
                    n)] = max(r_severity, cur_severity)
        return res

    def issue_dump_links(self, sg_list, rules: list[Rule], ext_things: set(), rule_severity: dict):
        res = []
        self.issue_linkid_by_rid = {}
        r: Rule
        for r in rules:
            rid = self.get_id_by_rule(r)
            severity = rule_severity.get(rid, 0)
            if severity == 0:
                continue
            sg: RuleGroupNG
            sg = self.sg_by_r(sg_list, r)
            if sg == None:
                continue
            self.issue_linkid_by_rid[rid] = set()
            id1_list = set()

            if len(sg.subnet_ids) == 0:
                id1_list = [self.get_id_by_sg(sg)]
            else:
                for subnet_id in sg.subnet_ids:
                    id1_list.add(self.get_id_by_net(
                        self.get_subnet_by_id(subnet_id)))
            nlist = []
            id2_list = set()
            ext_id = None
            if not r.is_any_addr() and self.is_known_address(r, self.nodes):
                nlist = self.filter_by_addr(r, self.nodes)
                for n in nlist:
                    id2_list.update(self.get_all_id_by_vm(n))
            else:
                for (ext_id, ip) in ext_things:
                    if ip == r.naddr:
                        break
                if ext_id == None:
                    # BUG
                    None
                id2_list.add(ext_id)
            for id1 in id1_list:
                for id2 in id2_list:
                    link_id = self.get_linkid_by_rule(r, id1, id2)
                    if self.linkid_in_res(res, link_id):
                        continue
                    if self.same_link_exist(res, id1, id2, severity):
                        continue
                    self.issue_linkid_by_rid[rid].add(link_id)
                    if r.egress == "True":
                        res.append({"id": link_id, "type": f"line{severity}", "dst": id1, "src": id2,
                                    "dstTooltip": "", "srcTooltip": ""})
                    else:
                        res.append({"id": link_id, "type": f"line{severity}", "dst": id2, "src": id1,
                                    "dstTooltip": "", "srcTooltip": ""})

        return res

    def issue_dump_scheme(self, sg_list,  ext_things: set(), node_severity, sg_severity, r_severity):
        c = {}
        c = {
            "children": []
        }
        # XXX Internet/External things
        for (id, ip) in ext_things:
            i = {
                "id": id,
                "type": "Cloud0",
                "label": ip,
                "iconTooltip": "External IP",
                "info": []
            }
            c["children"].append(i)
        for cloud in self.clouds:
            res = self.issue_dump_cloud(
                sg_list, cloud, node_severity, sg_severity, r_severity)
            c["children"].append(res)
        return c

    def issue_dump_cloud(self, sg_list, cloud: Cloud, node_severity, sg_severity, r_severity):
        c = {
            "children": []
        }
        c["id"] = self.get_id_by_cloud(cloud)
        c["label"] = cloud.name
        c["iconTooltip"] = cloud.cloud_type
        l = []
        a = "Cloud type"
        v = cloud.cloud_type
        i = "IconInfoCircle"
        l.append({"icon": i, "tooltip": f"{a}: {v}"})
        a = "Cloud region"
        v = cloud.aws_region
        i = "IconInfoCircle"
        l.append({"icon": i, "tooltip": f"{a}: {v}"})
        c["info"] = l
        max_severity = 0
        for sg in sg_list:
            if sg.cloud_id != cloud.id:
                continue
            severity = sg_severity.get(self.get_id_by_sg(sg), 0)
            for r in sg.rules:
                severity = max(severity, r_severity.get(
                    self.get_id_by_rule(r), 0))
            
            if len (sg.subnet_ids) == 0:
                res, sev = self.issue_dump_sg(
                    sg, severity, node_severity)
                c["children"].append(res)
                max_severity = max(sev, max_severity)           
            else:
                netlist = []
                for sn_id in sg.subnet_ids:
                    netlist.append(self.get_subnet_by_id(sn_id))
                for s in netlist:
                    res, sev = self.issue_dump_subnet(
                        s, severity, node_severity)
                    c["children"].append(res)
                    max_severity = max(sev, max_severity)
        c["type"] = f"Cloud{max_severity}"

        return c

    def issue_dump_sg(self, sg: RuleGroupNG, severity, node_severity: dict):
        c = {}
        c = {
            "children": []
        }
        sgid = self.get_id_by_sg(sg)
        c["id"] = sgid
        c["label"] = self.trim_ms_name(sg.name)
        c["iconTooltip"] = sg.name
        l = []
        c["info"] = l
        nlist = self.nodes_by_sg[sg]
        max_severity = severity
        for n in nlist:
            severity = node_severity.get(self.get_common_id_by_vm(n), 0)
            c["children"].append(self.issue_dump_nodes(
                n, severity))
            max_severity = max(max_severity, severity)
        c["type"] = f"Cloud{max_severity}"
        return c, max_severity

    def issue_dump_subnet(self, subnet: Subnet, severity, node_severity: dict):
        c = {
            "children": []
        }
        c["id"] = self.get_id_by_net(subnet)
        c["label"] = subnet.network
        c["iconTooltip"] = subnet.arn
        l = []
        c["info"] = l
        max_severity = severity
        for n in self.nodes:
            if n.subnet_id == subnet.name:
                severity = node_severity.get(self.get_common_id_by_vm(n), 0)
                c["children"].append(self.issue_dump_nodes(
                    n, severity))
                max_severity = max(severity, max_severity)
        c["type"] = f"Subnet{max_severity}"
        return c, max_severity

    def issue_dump_nodes(self, n: OneNode, severity):
        c = {}
        c = {
            "children": []
        }
        c["id"] = self.get_next_id_by_vm(n)
        c["type"] = f"VM{severity}"
        i = [
            ("Software", n.os),
            ("State", n.state),
            ("Public DNS", n.pubdn),
            ("Private DNS", n.privdn),
            ("Public IP", n.pubip),
            ("Private IP", n.privip),
            ("Name", n.name)
        ]
        c["label"] = self.generate_vm_label(i)
        c["info"] = [{"icon": n.type, "tooltip": n.name}]
        return c

    def get_next_id_by_vm(self, n: OneNode):
        if self.vm_count.get(f"{n.cloud_id}_{n.id}", None) == None:
            self.vm_count[f"{n.cloud_id}_{n.id}"] = 0
        self.vm_count[f"{n.cloud_id}_{n.id}"] += 1
        cnt = self.vm_count[f"{n.cloud_id}_{n.id}"]
        return f"VM_{n.cloud_id}_{n.id}_{cnt}"

    def get_all_id_by_vm(self, n: OneNode):
        res = []
        if self.vm_count.get(f"{n.cloud_id}_{n.id}", None) == None:
            return []
        cnt = self.vm_count[f"{n.cloud_id}_{n.id}"]
        for c in range(1, cnt + 1):
            res.append(f"VM_{n.cloud_id}_{n.id}_{c}")
        return res

    def get_common_id_by_vm(self, n: OneNode):
        return f"VM_{n.cloud_id}_{n.id}"

    def get_id_by_sg(self, sg: RuleGroupNG):
        return f"SG_{sg.cloud_id}_{sg.name}"

    def get_id_by_cloud(self, c: Cloud):
        return f"C_{c.id}"

    def get_id_by_net(self, n: Subnet):
        return f"Net_{n.name}"

    def get_id_by_rule(self, r: Rule):
        return f"Rule_{r.rule_id}"

    def get_linkid_by_rule(self, r: Rule, id1, id2):
        return f"rule_{r.id}_src_{id1}_dst_{id2}"

    def is_sg_acl(self, sg: RuleGroupNG):
        return sg.name.find("acl-") == 0

    def get_subnet_by_id(self, subnet_id):
        n: Subnet
        for n in self.subnets:
            if n.name == subnet_id:
                return n
        return None

    def generate_vm_label(self, lav: list):
        label = ""
        linefeed = ""
        for (a, v) in lav:
            if v == "" or v == None:
                continue
            label += f"{linefeed}{a}: {v}"
            linefeed = "<br/>"
        return label

    def linkid_in_res(self, res, link_id):
        for i in res:
            if i['id'] == link_id:
                return True
        return False

    def same_link_exist(self, res, id1, id2, severity):
        for i in res:
            if i['type'] != f"line{severity}":
                continue
            if set([id1, id2]) != set([i['src'], i['dst']]):
                continue
            return True
        return False

    def trim_ms_name(self, n: str):
        return n.split("/")[-1]
