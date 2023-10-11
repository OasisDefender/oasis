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
from s3_bucket  import S3_Bucket

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

            acl_response = client.describe_network_acls(Filters=[{'Name': 'association.subnet-id', 'Values': [row['SubnetId']]}])
            for acl in acl_response['NetworkAcls']:
                subnet_rg = RuleGroup(id = None,
                                subnet_id=subnet.name,
                                name     = acl['NetworkAclId'],
                                type     = 'NSG',
                                cloud_id = cloud_id)
                subnet_rg.id = db.add_rule_group(rule_group=subnet_rg.to_sql_values())
                # Load rules for current rule group
                self.get_network_acl_rules(cloud_id, acl['NetworkAclId'])
            

        response = client.describe_instances()
        for res in response['Reservations']:
            for instance in res['Instances']:
                pubip: str = None
                try:
                    pubip = instance["PublicIpAddress"]
                except KeyError:
                    pubip = None
                #print(f"instance: {instance}")
                
                # Dont load terminated VM
                if instance['State']['Name'] == 'terminated':
                    continue

                vm = VM(vm=None, type='VM',
                        vpc_id=instance['VpcId'],
                        azone=instance['Placement']['AvailabilityZone'],
                        subnet_id=instance['SubnetId'],
                        name=instance['InstanceId'],
                        privdn=null_empty_str(instance['PrivateDnsName']),
                        privip=null_empty_str(instance['PrivateIpAddress']),
                        pubdn=null_empty_str(instance['PublicDnsName']),
                        pubip=null_empty_str(pubip),
                        note=instance['Tags'][0]['Value'] if 'Tags' in instance and len(instance['Tags']) > 0 else instance['InstanceId'],
                        os=instance['PlatformDetails'],
                        state=unify_state(instance['State']['Name']),
                        mac=instance['NetworkInterfaces'][0]['MacAddress'].lower().replace('-', ':'),
                        if_id=instance['NetworkInterfaces'][0]['NetworkInterfaceId'], cloud_id=cloud_id)
                vm.id = db.add_instance(instance=vm.to_sql_values())
                for fw in instance["NetworkInterfaces"][0]["Groups"]:
                    rg = RuleGroup(id       = None,
                                   if_id    = instance['NetworkInterfaces'][0]['NetworkInterfaceId'],
                                   name     = fw['GroupId'],
                                   type     = 'NSG',
                                   cloud_id = cloud_id)
                    rg.id = db.add_rule_group(rule_group=rg.to_sql_values())
                    # Load rules for current rule group
                    self.get_group_rules(cloud_id, fw['GroupId'])
        
        # Load IGWs, Use nodes table for store
        response = client.describe_internet_gateways()
        for res in response["InternetGateways"]:
            try:
                desc = res["Tags"][0]["Value"]
            except KeyError:
                desc = "none"
            except IndexError:
                desc = "none"
            igw = VM(vm=None, type='IGW',
                    vpc_id=res["Attachments"][0]["VpcId"],
                    azone='',
                    subnet_id='',
                    name=res["InternetGatewayId"],
                    privdn='',
                    privip='',
                    pubdn='',
                    pubip='',
                    note=desc,
                    os='',
                    state=res["Attachments"][0]["State"],
                    mac='',
                    if_id='',
                    cloud_id=cloud_id)
            igw.id = db.add_instance(instance=igw.to_sql_values())
        
        # Load NATs. Use nodes table for store
        response = client.describe_nat_gateways()
        for res in response["NatGateways"]:
            try:
                desc = res["Tags"][0]["Value"]
            except KeyError:
                desc = "none"
            except IndexError:
                desc = "none"
            nat = VM(vm=None, type='NAT',
                    vpc_id=res["VpcId"],
                    azone='',
                    subnet_id=res["SubnetId"],
                    name=res["NatGatewayId"],
                    privdn='',
                    privip=res["NatGatewayAddresses"][0]["PrivateIp"],
                    pubdn='',
                    pubip=res["NatGatewayAddresses"][0]["PublicIp"],
                    note=desc,
                    os='',
                    state=res["State"],
                    mac='',
                    if_id=res["NatGatewayAddresses"][0]["NetworkInterfaceId"],
                    cloud_id=cloud_id)
            nat.id = db.add_instance(instance=nat.to_sql_values())

            # Load ELBs. Use nodes table for store
            elbv2_client = self.__session.client('elbv2')
            response     = elbv2_client.describe_load_balancers()
            elbs         = response['LoadBalancers']
            while 'NextMarker' in response:
                response = elbv2_client.describe_load_balancers(Marker=response['NextMarker'])
                elbs.extend(response['LoadBalancers'])
            for res in elbs:
                for azone in res["AvailabilityZones"]:
                    elb_if_id = f"{res['LoadBalancerArn']}-{azone['SubnetId']}-{azone['ZoneName']}"
                    elb = None
                    if res['Scheme'] == 'internal':
                        elb = VM(vm=None, type='ELB',
                                vpc_id    = res["VpcId"],
                                azone     = azone["ZoneName"],
                                subnet_id = azone["SubnetId"],
                                name      = res["LoadBalancerName"],
                                privdn    = res["DNSName"],
                                privip    = '',
                                pubdn     = '',
                                pubip     = '',
                                note      = res["Type"],
                                os        = '',
                                state     = res["State"]["Code"],
                                mac       = '',
                                if_id     = elb_if_id,
                                cloud_id  = cloud_id)
                    else:
                        elb = VM(vm=None, type='ELB',
                                vpc_id    = res["VpcId"],
                                azone     = azone["ZoneName"],
                                subnet_id = azone["SubnetId"],
                                name      = res["LoadBalancerName"],
                                privdn    = '',
                                privip    = '',
                                pubdn     = res["DNSName"],
                                pubip     = '',
                                note      = res["Type"],
                                os        = '',
                                state     = res["State"]["Code"],
                                mac       = '',
                                if_id     = elb_if_id,
                                cloud_id  = cloud_id)
                    elb.id = db.add_instance(instance=elb.to_sql_values())
                elb_describe_response = elbv2_client.describe_load_balancers(LoadBalancerArns=[res["LoadBalancerArn"]])
                lb = elb_describe_response['LoadBalancers'][0]
                lb_sgs = lb.get('SecurityGroups', [])
                for lb_sg in lb_sgs:
                    rg = RuleGroup(id       = None,
                                   if_id    = elb_if_id,
                                   name     = lb_sg,
                                   type     = 'NSG',
                                   cloud_id = cloud_id)
                    rg.id = db.add_rule_group(rule_group=rg.to_sql_values())
                    # Load rules for current rule group
                    self.get_group_rules(cloud_id, lb_sg)
            
            # Load RDSs. Use nodes table for store
            rds_client = self.__session.client('rds')
            response   = rds_client.describe_db_instances()
            for res in response['DBInstances']:
                for rds_subnet in res['DBSubnetGroup']['Subnets']:
                    rds_if_id = f"{rds_subnet['SubnetIdentifier']}-{rds_subnet['SubnetAvailabilityZone']['Name']}"
                    if res['PubliclyAccessible'] == 'False':
                        rds = VM(vm=None,
                                type      = 'RDS',
                                vpc_id    = res['DBSubnetGroup']['VpcId'],
                                azone     = res['AvailabilityZone'],
                                subnet_id = rds_subnet['SubnetIdentifier'],
                                name      = res['DBInstanceIdentifier'],
                                privdn    = res['Endpoint']['Address'],
                                privip    = '',
                                pubdn     = '',
                                pubip     = '',
                                note      = res['DBSubnetGroup']['DBSubnetGroupDescription'],
                                os        = f"{res['Engine']}: {res['EngineVersion']}",
                                state     = res['DBInstanceStatus'],
                                mac       = '',
                                if_id     = rds_if_id,
                                cloud_id  = cloud_id)
                    else:
                        rds = VM(vm=None,
                                type      = 'RDS',
                                vpc_id    = res['DBSubnetGroup']['VpcId'],
                                azone     = res['AvailabilityZone'],
                                subnet_id = rds_subnet['SubnetIdentifier'],
                                name      = res['DBInstanceIdentifier'],
                                privdn    = '',
                                privip    = '',
                                pubdn     = res['Endpoint']['Address'],
                                pubip     = '',
                                note      = res['DBSubnetGroup']['DBSubnetGroupDescription'],
                                os        = f"{res['Engine']}: {res['EngineVersion']}",
                                state     = res['DBInstanceStatus'],
                                mac       = '',
                                if_id     = rds_if_id,
                                cloud_id  = cloud_id)
                    rds.id = db.add_instance(instance=rds.to_sql_values())
                # Load RDS SG
                for rds_sg in res['VpcSecurityGroups']:
                    rg = RuleGroup(id       = None,
                                   if_id    = rds_if_id,
                                   name     = rds_sg['VpcSecurityGroupId'],
                                   type     = 'NSG',
                                   cloud_id = cloud_id)
                    rg.id = db.add_rule_group(rule_group=rg.to_sql_values())
                    # Load rules for current rule group
                    self.get_group_rules(cloud_id, rds_sg['VpcSecurityGroupId'])

        # Load S3 Buckets
        s3_client = self.__session.resource('s3')
        for bucket in s3_client.buckets.all():
            bucket = S3_Bucket(id    = None,
                            name     = bucket.name,
                            cloud_id = cloud_id)
            bucket.id = db.add_s3_bucket(bucket=bucket.to_sql_values())

        return 0
    


    def get_group_rules(self, cloud_id: int, group_id: str):
        db     = DB()
        naddr  = None
        ref_sg = None
        prefix_list_id  = None

        res_client = self.__session.resource('ec2')
        client     = self.__session.client('ec2')

        response = client.describe_security_group_rules(Filters=[{'Name': 'group-id', 'Values': [group_id]}])
        priority : int = 0
        for rule in response['SecurityGroupRules']:
            # Rule with reference to prefix list
            try:
                prefix_list_id = rule["PrefixListId"]
                prefix_list = client.get_managed_prefix_list_entries(PrefixListId = prefix_list_id)
                for prefix in prefix_list['Entries']:
                    naddr = prefix['Cidr']
                    if naddr.split('/')[-1] == '32':
                        naddr = naddr.split('/')[0]
                    priority = priority + 1
                    r = Rule(id=None,
                            group_id=rule['GroupId'],
                            rule_id=rule['SecurityGroupRuleId'],
                            egress=rule['IsEgress'],
                            proto=rule['IpProtocol'].upper().replace('-1', 'ANY'),
                            port_from=rule['FromPort'],
                            port_to=rule['ToPort'],
                            naddr=naddr,
                            cloud_id=cloud_id,
                            ports=make_ports_string(rule['FromPort'], rule['ToPort'], rule['IpProtocol']),
                            action='allow',
                            priority=priority)
                    r.id = db.add_rule(rule=r.to_sql_values())
                    #print(r.to_sql_values())
                continue
            except KeyError:
                pass

            # Rule with reference to other SG
            try:
                ref_sg = rule["ReferencedGroupInfo"]["GroupId"]
                ref_sg_instances = res_client.instances.filter(
                    Filters=[
                        {
                            'Name': 'instance.group-id',
                            'Values': [ref_sg]
                        }
                    ]
                )
                for ref_sg_instance in ref_sg_instances:
                    naddr = None
                    for network_interface in ref_sg_instance.network_interfaces:
                        for private_ip in network_interface.private_ip_addresses:
                            naddr = private_ip['PrivateIpAddress']
                            if naddr == "":
                                naddr = None
                                continue
                            if naddr.split('/')[-1] == '32':
                                naddr = naddr.split('/')[0]
                            priority = priority + 1
                            r = Rule(id       = None,
                                    group_id  = rule['GroupId'],
                                    rule_id   = rule['SecurityGroupRuleId'],
                                    egress    = rule['IsEgress'],
                                    proto     = rule['IpProtocol'].upper().replace('-1', 'ANY'),
                                    port_from = rule['FromPort'],
                                    port_to   = rule['ToPort'],
                                    naddr     = naddr,
                                    cloud_id  = cloud_id,
                                    ports=make_ports_string(rule['FromPort'], rule['ToPort'], rule['IpProtocol']),
                                    action='allow',
                                    priority=priority)
                            r.id = db.add_rule(rule=r.to_sql_values())
                            if naddr != None: # TODO: remove for many network interfaces support
                                break
                        if naddr != None: # TODO: remove for many network interfaces support
                            break
                continue
            except KeyError:
                pass

            # Classic rule with ip/mask and port(s)
            try:
                naddr = rule["CidrIpv4"]
            except KeyError:
                naddr = ""
            if naddr == "":
                naddr = "0.0.0.0/0"
            if naddr.split('/')[-1] == '32':
                naddr = naddr.split('/')[0]
            priority = priority + 1
            r = Rule(id=None,
                    group_id=rule['GroupId'],
                    rule_id=rule['SecurityGroupRuleId'],
                    egress=rule['IsEgress'],
                    proto=rule['IpProtocol'].upper().replace('-1', 'ANY'),
                    port_from=rule['FromPort'],
                    port_to=rule['ToPort'],
                    naddr=naddr,
                    cloud_id=cloud_id,
                    ports=make_ports_string(rule['FromPort'], rule['ToPort'], rule['IpProtocol']),
                    action='allow',
                    priority=priority)
            r.id = db.add_rule(rule=r.to_sql_values())
            #print(r.to_sql_values())



    def get_network_acl_rules(self, cloud_id: int, group_id: str):
        db     = DB()
        naddr  = None

        client = self.__session.client('ec2')
        response = client.describe_network_acls(Filters=[{'Name': 'association.network-acl-id', 'Values': [group_id]}])
        for acl in response['NetworkAcls']:
            for rule in acl['Entries']:
                try:
                    naddr = rule["CidrBlock"]
                except KeyError:
                    naddr = ""
                if naddr == "":
                    naddr = "0.0.0.0/0"
                if naddr.split('/')[-1] == '32':
                    naddr = naddr.split('/')[0]
                
                port_from : str = None
                port_to   : str = None
                try:
                    port_from = rule['PortRange']['From']
                    port_to   = rule['PortRange']['To']
                except KeyError:
                    try:
                        port_from = rule['IcmpTypeCode']['Code']
                        port_to   = rule['IcmpTypeCode']['Type']
                    except KeyError:
                        pass
                
                proto: str = ''
                if rule['Protocol'] == '-1':
                    proto = 'ANY'
                elif rule['Protocol'] == '1':
                    proto = 'ICMP'
                elif rule['Protocol'] == '6':
                    proto = 'TCP'
                elif rule['Protocol'] == '17':
                    proto = 'UDP'
                else:
                    proto = rule['Protocol']
                
                r = Rule(id=None,
                         group_id=group_id,
                         rule_id=acl['NetworkAclId'],
                         egress=rule['Egress'],
                         proto=proto,
                         port_from=port_from,
                         port_to=port_to,
                         naddr=naddr,
                         cloud_id=cloud_id,
                         ports=make_ports_string(port_from, port_to, proto),
                         action=rule['RuleAction'],
                         priority=rule['RuleNumber'])
                r.id = db.add_rule(rule=r.to_sql_values())



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

        # Unsupported protocol
        if not response:
            return True
        
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
