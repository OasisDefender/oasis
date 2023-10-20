from ipaddress import ip_network
from .cloud import Cloud
from .vpc import VPC
from .subnet import Subnet
from .vm import VM
from .rule_group import RuleGroup
from .rule import Rule


class EffectiveRulelist:
    def __init__(self, cloud: Cloud, vpcs: list[VPC], sgs: list[RuleGroup], rules: list[Rule]):
        # for each vpc
        #   1 add vm it to dictianary with id key
        #   2 for each vm
        #     3 add applicable rules from subnet
        #     4 for each vm sg
        #       5 add applicable rule from sg
        self.vms_er = {}
        for vpc in vpcs:
            for subnet in vpc.subnets:
                for vm in subnet.vms:
                    vm_rules = []
                    for sg in sgs:
                        if sg.if_id != vm.if_id:
                            continue
                        if sg.subnet_id != subnet.id:
                            continue
                        for rule in rules:
                            if self.is_applicable(vm, rule):
                                vm_rules.append(rule)
                    crosses = self.check_crosses(vm_rules)
                    bp = self.check_best_practice(vm_rules)
                    self.vms_er[(cloud.id, vpc.id, subnet.id, vm.id)] = {
                        'Rules': vm_rules, 'Crosses': crosses, 'Best Practice Warnings': bp}

    def is_applicable(self, vm: VM, rule: Rule):
        return True

    def check_crosses(self, vm_rules):
        #   1. for each rule in rule list
        #     2. find crossed rules
        #      3. add found rules to cross list in vms_er_dict
        res = {}
        for key_rule in vm_rules:
            for rule in vm_rules:
                if key_rule.id == rule.id:
                    continue
                if key_rule.proto == rule.proto and key_rule.egress == rule.egress and \
                   not (key_rule.port_to < rule.port_from or key_rule.port_from > rule.port_to) and \
                   ip_network(key_rule.naddr).overlapped(ip_network(rule.naddr)):
                    res[key_rule].append(rule)
        for kr1 in vm_rules:
            for kr2 in vm_rules:
                if set(res[kr1]) == set(res[kr2]):
                    del res[kr2]
        return res

    def get_effective_rules(self):
        return self.vms_er

    def check_best_practice(vm_rules):
        return {}
