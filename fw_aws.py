import boto3
import botocore.exceptions
import sys
import json

from db         import DB
#from cloud      import Cloud
from vpc        import VPC
from subnet     import Subnet
from vm         import VM
from rule_group import RuleGroup
from rule       import Rule
from fw_common  import get_tag_value, unify_state, null_empty_str, make_ports_string

from types  import SimpleNamespace

class FW_AWS:
    def __init__(self):
        self.__cloud_id: int                   = 0
        self.__session:  boto3.session.Session = None
        self.__db:       DB                    = DB()


    def connect(self, cloud_id: int) -> int:
        db = DB()
        creds = self.__db.get_aws_credentials(cloud_id)
        for cred in creds:
            self.__session = boto3.Session(aws_access_key_id=cred[1], aws_secret_access_key=cred[2], region_name=cred[0])
            self.__cloud_id = cloud_id
            break
        # Test connection
        try:
            client = self.__session.client('ec2')
            response = client.describe_vpcs()
            for row in response['Vpcs']:
                break
        except:
            self.__cloud_id = 0 #"AWS: cant connect to cloud!"
        return self.__cloud_id


    def get_topology(self, cloud_id: int):
        db = DB()
        client = self.__session.client('ec2')
        vpc_note: str = None
        response = client.describe_vpcs()
        for row in response['Vpcs']:
            vpc_note = get_tag_value(row)
            if vpc_note == "none":
                vpc_note = row['VpcId']

            vpc = VPC(vpc=None, name=row['VpcId'], network=row['CidrBlock'], cloud_id=cloud_id, note=vpc_note)
            vpc.id = db.add_vpc(vpc=vpc.to_sql_values())
        
        subnet_note: str = None
        response = client.describe_subnets()
        for row in response['Subnets']:
            subnet_note = get_tag_value(row)
            if subnet_note == "none":
                subnet_note = row['SubnetId']
            subnet = Subnet(subnet=None, name=row['SubnetId'], arn=row['SubnetArn'], network=row['CidrBlock'],
                            azone=row['AvailabilityZone'], note=subnet_note,
                            vpc_id=row['VpcId'], cloud_id=cloud_id)
            subnet.id = db.add_subnet(subnet=subnet.to_sql_values())

        response = client.describe_instances()
        for res in response['Reservations']:
            for instance in res['Instances']:
                pubip: str = None
                try:
                    pubip = instance["PublicIpAddress"]
                except KeyError:
                    pubip = None
                vm = VM(vm=None, type='VM',
                        vpc_id=instance['VpcId'],
                        azone=instance['Placement']['AvailabilityZone'],
                        subnet_id=instance['SubnetId'],
                        name=instance['InstanceId'],
                        privdn=null_empty_str(instance['PrivateDnsName']),
                        privip=null_empty_str(instance['PrivateIpAddress']),
                        pubdn=null_empty_str(instance['PublicDnsName']),
                        pubip=null_empty_str(pubip),
                        note=instance['Tags'][0]['Value'],
                        os=instance['PlatformDetails'],
                        state=unify_state(instance['State']['Name']),
                        mac=instance['NetworkInterfaces'][0]['MacAddress'].lower().replace('-', ':'),
                        if_id=instance['NetworkInterfaces'][0]['NetworkInterfaceId'], cloud_id=cloud_id)
                vm.id = db.add_instance(instance=vm.to_sql_values())
                for fw in instance["NetworkInterfaces"][0]["Groups"]:
                    rg = RuleGroup(id=None,
                                   if_id=instance['NetworkInterfaces'][0]['NetworkInterfaceId'],
                                   name=fw['GroupId'],
                                   cloud_id=cloud_id)
                    rg.id = db.add_rule_group(rule_group=rg.to_sql_values())
                    # Load rules for current rule group
                    self.get_group_rules(cloud_id, fw['GroupId'])
        return 0
    


    def get_group_rules(self, cloud_id: int, group_id: str):
        db = DB()
        client = self.__session.client('ec2')
        response = client.describe_security_group_rules()
        for rule in response['SecurityGroupRules']:
            if rule['GroupId'] == group_id:
                try:
                    naddr = rule["CidrIpv4"]
                except KeyError:
                    naddr = ""
                if naddr == "":
                    naddr = "0.0.0.0/0"
                if naddr.split('/')[-1] == '32':
                    naddr = naddr.split('/')[0]
                r = Rule(id=None,
                        group_id=rule['GroupId'],
                        rule_id=rule['SecurityGroupRuleId'],
                        egress=rule['IsEgress'],
                        proto=rule['IpProtocol'].upper().replace('-1', 'ANY'),
                        port_from=rule['FromPort'],
                        port_to=rule['ToPort'],
                        naddr=naddr,
                        cloud_id=cloud_id,
                        ports=make_ports_string(rule['FromPort'], rule['ToPort'], rule['IpProtocol']))
                r.id = db.add_rule(rule=r.to_sql_values())
                #print(r.to_gui_dict())



    def add_rule(self, rule: Rule, group_id: str) -> bool:
        response: dict = None
        client         = self.__session.client('ec2')

        port_from: int = 0
        try:
            port_from = int(rule.port_from)
        except:
            port_from = 0

        port_to:   int = 0
        try:
            port_to = int(rule.port_to)
        except:
            port_to = 0

        #print(rule.to_sql_values())
        try:
            if rule.egress == 'outbound':
                if rule.proto.upper() == 'TCP' or rule.proto.upper() == 'UDP':
                    response = client.authorize_security_group_egress(
                                            GroupId = group_id,
                                            IpPermissions = [
                                                {
                                                    'IpProtocol' : rule.proto,
                                                    'IpRanges'   : [{'CidrIp': rule.naddr}],
                                                    'FromPort'   : port_from,
                                                    'ToPort'     : port_from if port_to == 0 else port_to
                                                },
                                            ]
                                        )

                if rule.proto.upper() == 'ICMP':
                    response = client.authorize_security_group_egress(
                                            GroupId = group_id,
                                            IpPermissions = [
                                                {
                                                    'IpProtocol' : rule.proto,
                                                    'IpRanges'   : [{'CidrIp': rule.naddr}],
                                                    'FromPort'   : port_from,
                                                    'ToPort'     : port_to
                                                },
                                            ]
                                        )

            if rule.egress == 'inbound':
                if rule.proto.upper() == 'TCP' or rule.proto.upper() == 'UDP':
                    response = client.authorize_security_group_ingress(
                                            GroupId = group_id,
                                            IpPermissions = [
                                                {
                                                    'IpProtocol' : rule.proto,
                                                    'IpRanges'   : [{'CidrIp': rule.naddr}],
                                                    'FromPort'   : port_from,
                                                    'ToPort'     : port_from if port_to == 0 else port_to
                                                },
                                            ]
                                        )

                if rule.proto.upper() == 'ICMP':
                    response = client.authorize_security_group_ingress(
                                            GroupId = group_id,
                                            IpPermissions = [
                                                {
                                                    'IpProtocol' : rule.proto,
                                                    'IpRanges'   : [{'CidrIp': rule.naddr}],
                                                    'FromPort'   : port_from,
                                                    'ToPort'     : port_to
                                                },
                                            ]
                                        )

        except botocore.exceptions.ClientError as error:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error while add rule: {rule.to_dict()}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Error message: {error.response['Error']['Message']}")
            return False

        

        #print(response)
        return type(response['Return'])


    def del_rule(self, rule: Rule) -> bool:
        status: bool   = False
        response: dict = None
        client         = self.__session.client('ec2')
        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: Try delete rule: {rule.to_dict()}")
        if rule.egress == 'False':
            response = client.revoke_security_group_ingress(
                GroupId=rule.group_id,
                SecurityGroupRuleIds=[rule.rule_id]
            )
        else:
            response = client.revoke_security_group_egress(
                GroupId=rule.group_id,
                SecurityGroupRuleIds=[rule.rule_id]
            )
        #print(f"response: {response}")
        return type(response['Return'])
