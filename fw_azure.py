import sys
import uuid

from azure.identity            import *
from azure.mgmt.resource       import ResourceManagementClient
from azure.mgmt.compute        import ComputeManagementClient
from azure.mgmt.network        import NetworkManagementClient
from azure.mgmt.network.models import SecurityRule
from azure.core.exceptions     import *

from db         import DB
from vpc        import VPC
from subnet     import Subnet
from vm         import VM
from rule_group import RuleGroup
from rule       import Rule
from fw_common  import make_ports_string

class FW_Azure:
    def __init__(self):
        self.__cloud_id        = ""
        self.__db              = DB()

        self.__resource_client = None
        self.__compute_client = None
        self.__network_client = None


    def __get_unique_priority(self, resource_group_name, nsg_name) -> int:
        unique_priority: int = -1
        max_priority:    int = 0

        existing_rules = self.__network_client.security_rules.list(resource_group_name, nsg_name)
        try:
            max_priority = max(rule.priority for rule in existing_rules) if existing_rules else 0
        except ValueError:
            max_priority = 0

        if max_priority == 0:
            unique_priority = 100
        else:
            unique_priority = max_priority + 1

        if unique_priority > 4096:
            unique_priority = -1
        
        return unique_priority


    
    def connect(self, cloud_id: int) -> int:
        db = DB()
        creds = self.__db.get_azure_credentials(cloud_id)
        for cred in creds:
            credential             = ClientSecretCredential(cred[0], cred[1], cred[2])
            self.__resource_client = ResourceManagementClient(credential, cred[3])
            self.__compute_client  = ComputeManagementClient (credential, cred[3])
            self.__network_client  = NetworkManagementClient (credential, cred[3])
            self.__cloud_id        = cloud_id
            break

        # Test connection
        vpcs = self.__network_client.virtual_networks.list_all()
        try:
            for vpc in vpcs:
                break
        except:
            self.__cloud_id = 0

        return self.__cloud_id


    def get_topology(self, cloud_id: int):
        db = DB()
        # Load VPC's
        vpcs = self.__network_client.virtual_networks.list_all()
        for vpc in vpcs:
            v = VPC(vpc=None, name=vpc.name, network=vpc.address_space.address_prefixes[0], cloud_id=cloud_id, note=vpc.name)
            v.id = db.add_vpc(vpc=v.to_sql_values())
            # Load Subnet's
            for subnet in vpc.subnets:
                s = Subnet(subnet=None, name=subnet.name, arn=subnet.id, network=subnet.address_prefix,
                                azone='', note=subnet.name, vpc_id=vpc.name, cloud_id=cloud_id)
                s.id = db.add_subnet(subnet=s.to_sql_values())
            # Load VM's
            vms = self.__compute_client.virtual_machines.list_all()
            for vm in vms:
                nic_id       = vm.network_profile.network_interfaces[0].id
                if_id        = nic_id.split('/')[-1]

                resource_group_name = vm.id.split('/')[4]
                vm_info      = self.__compute_client.virtual_machines.instance_view(resource_group_name, vm.name)
                state        = vm_info.statuses[-1].display_status

                nic          = self.__network_client.network_interfaces.get(resource_group_name, if_id)
                mac          = nic.mac_address
                privip       = nic.ip_configurations[0].private_ip_address

                pubip        = ""
                pubdn        = ""
                if nic.ip_configurations[0].public_ip_address:
                    public_ip_address = self.__network_client.public_ip_addresses.get(
                            resource_group_name,
                            nic.ip_configurations[0].public_ip_address.id.split('/')[-1]
                        )
                    pubip     = public_ip_address.ip_address
                    if public_ip_address.dns_settings:
                        pubdn = public_ip_address.dns_settings.fqdn

                subnet_id     = nic.ip_configurations[0].subnet.id.split('/')[-1]

                v = VM(vm=None,
                        type='VM',
                        vpc_id=vpc.id.split('/')[-1],
                        azone=vm.location,
                        subnet_id=subnet_id,
                        name=vm.id,
                        privdn=vm.os_profile.computer_name,
                        privip=privip,
                        pubdn=pubdn,
                        pubip=pubip,
                        note=vm.name,
                        os='Linux' if vm.os_profile.windows_configuration == "None" else 'Windows',
                        state=state,
                        mac=mac,
                        if_id=if_id,
                        cloud_id=cloud_id)
                v.id = db.add_instance(instance=v.to_sql_values())
                # Load Rule Group's
                vm_resource_group_name = vm.id.split('/')[4]
                vm_nic                 = self.__network_client.network_interfaces.get(
                                            vm_resource_group_name,
                                            vm.network_profile.network_interfaces[0].id.split('/')[-1])
                if nic.network_security_group:
                    rg = RuleGroup(id=None,
                                   if_id=vm.network_profile.network_interfaces[0].id.split('/')[-1],
                                   name=nic.network_security_group.id,
                                   cloud_id=cloud_id)
                    rg.id = db.add_rule_group(rule_group=rg.to_sql_values())
                    # Load rules for current rule group
                    self.get_group_rules(cloud_id, nic.network_security_group.id)
        return 0



    def get_group_rules(self, cloud_id: int, group_id: str):
        db = DB()
        resource_groups = self.__resource_client.resource_groups.list()
        for rg in resource_groups:
            resource_group_name = rg.id.split('/')[-1]
            rules = self.__network_client.security_rules.list(resource_group_name, group_id.split('/')[-1])
            try:
                for rule in rules:
                    if rule.direction == 'Inbound': # Inbound rules
                        r = Rule(id=None,
                                group_id=group_id,
                                rule_id=rule.id,
                                egress='False',
                                proto=rule.protocol.upper().replace("-1", "ANY"),
                                port_from=rule.destination_port_range,
                                port_to='',
                                naddr=rule.source_address_prefix.replace("*", "0.0.0.0/0"),
                                cloud_id=cloud_id,
                                ports=make_ports_string(rule.destination_port_range, rule.destination_port_range, rule.protocol)
                            )
                    else:                           # Outbound rules
                        r = Rule(id=None,
                                group_id=group_id,
                                rule_id=rule.id,
                                egress='True',
                                proto=rule.protocol.upper().replace("-1", "ANY"),
                                port_from=rule.destination_port_range,
                                port_to='',
                                naddr=rule.destination_address_prefix.replace("*", "0.0.0.0/0"),
                                cloud_id=cloud_id,
                                ports=make_ports_string(rule.destination_port_range, rule.destination_port_range, rule.protocol)
                            )
                    r.id = db.add_rule(rule=r.to_sql_values())
                    #print(r.to_gui_dict())
            except:
                pass #print(f"no rules in {resource_group_name}/{group_id.split('/')[-1]}")



    def add_rule(self, rule: Rule, group_id: str) -> bool:
        security_rule_name = f"bfw-{uuid.uuid4()}"

        resource_group_name = group_id.split('/')[4]
        nsg_name            = group_id.split('/')[-1]

        rule_num = self.__get_unique_priority(resource_group_name, nsg_name)
        if rule_num < 0:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error while add rule: {rule.to_dict()}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error message: Maximum rule number exided!")
            return False

        rule_ports: str = rule.ports
        if rule_ports == '':
            rule_ports = '*'

        try:
            if rule.egress == 'inbound':
                if rule.proto.upper() == 'TCP' or rule.proto.upper() == 'UDP':
                    security_rule_params = SecurityRule(
                        protocol=rule.proto,
                        source_address_prefix=rule.naddr,
                        destination_address_prefix='*',
                        source_port_range='*',
                        destination_port_range=rule_ports,
                        access='Allow',
                        priority=rule_num,
                        direction='Inbound',
                        description=security_rule_name,
                    )
                if rule.proto.upper() == 'ICMP':
                    security_rule_params = SecurityRule(
                        protocol=rule.proto,
                        source_address_prefix=rule.naddr,
                        destination_address_prefix='*',
                        source_port_range='*',
                        destination_port_range='*',
                        access='Allow',
                        priority=rule_num,
                        direction='Inbound',
                        description=security_rule_name,
                    )

            if rule.egress == 'outbound':
                if rule.proto.upper() == 'TCP' or rule.proto.upper() == 'UDP':
                    security_rule_params = SecurityRule(
                        protocol=rule.proto,
                        source_address_prefix='*',
                        destination_address_prefix=rule.naddr,
                        source_port_range='*',
                        destination_port_range=rule_ports,
                        access='Allow',
                        priority=rule_num,
                        direction='Outbound',
                        description=security_rule_name,
                    )

                if rule.proto.upper() == 'ICMP':
                    security_rule_params = SecurityRule(
                        protocol=rule.proto,
                        source_address_prefix='*',
                        destination_address_prefix=rule.naddr,
                        source_port_range='*',
                        destination_port_range='*',
                        access='Allow',
                        priority=rule_num,
                        direction='Outbound',
                        description=security_rule_name,
                    )

            result = self.__network_client.security_rules.begin_create_or_update(
                resource_group_name,
                nsg_name,
                security_rule_name,
                security_rule_params
            )
            result.wait()
            if result.status() != 'Succeeded':
                print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error while add rule: {rule.to_dict()}")
                return False


        except azure.core.exceptions.ResourceExistsError:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error message: {error.response['Error']['Message']}")
        except:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error while add rule: {rule.to_dict()}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error message: {error.response['Error']['Message']}")
            return False

        return True



    def del_rule(self, rule: Rule) -> bool:
        status: bool = False
        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Try delete rule: {rule.to_dict()}")

        resource_group_name = rule.group_id.split('/')[4]
        nsg_name            = rule.group_id.split('/')[-1]
        rule_name           = rule.rule_id.split('/')[-1]

        result = self.__network_client.security_rules.begin_delete(resource_group_name, nsg_name, rule_name)
        result.wait()

        if result.status() == 'Succeeded':
            status = True
        else:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error while del rule: {rule_name}")

        return status

