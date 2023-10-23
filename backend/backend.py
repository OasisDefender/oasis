import json

from .ctx import CTX  # base class for frontend objects
from .cloud import Cloud
from .db import DB
from .cloud_map import CloudMap, cloud_map_encoder
from .internet_nodes import InternetNodes, internet_nodes_encoder
from .links import Links, link_encoder
from .fw_aws import FW_AWS
from .fw_azure import FW_Azure
from .fw import FW_Selected, FW_Selected_encoder
from .vm_rules import VM_Rules
from .s3_bucket import S3_Bucket, S3_Cloud
from .classifiers_list import classifier
from .split_vms import attr_set, split_vms
from .rule_group import RuleGroup, get_all_rule_groups
from .rule import Rule, get_all_rules
from .vm import Nodes
from .links_by_rules import links_by_rules
from .global_settings import DEMO_MODE


class Backend(CTX):
    def __init__(self):
        pass

    def __db_exist(self, user_id: str = None):
        return db_exist(user_id)

    def get_clouds(self):
        status: int = 200
        body = None
        try:
            db = DB(user_id=self.get_ctx())
            clouds = db.get_clouds()
            body = [c.to_dict() for c in clouds]
        except:
            status = 500
            body = {'message': "Database error"}
        return status, body

    def cloud_sync(self, id: int):
        fw = None
        context = DB(user_id=self.get_ctx())
        body = None
        status = 200
        cloud: Cloud = None
        try:
            for cloud in context.get_clouds():
                if cloud.id == id:
                    if cloud.cloud_type == 'AWS':
                        fw = FW_AWS(_db=context)
                        break
                    if cloud.cloud_type == 'AZURE':
                        fw = FW_Azure(_db=context)
                        break
                    status = 500
                    body = {
                        'message': f"Cloud Type: '{cloud.cloud_type}' - not supported!"}
            if fw != None:
                fw.save_ctx(self.get_ctx())
                context.sync_cloud(cloud.id)
                fw.connect(cloud.id)
                fw.get_topology(cloud.id)
        except:
            status = 500
            body = {'message': "Cloud sync error"}
        return status, body

    def cloud_delete(self, id: int):
        body = None
        status = 200
        try:
            db = DB(self.user_id)
            db.delete_cloud(id)
        except:
            status = 500
            body = {'message': "Database error"}
        return status, body

    def cloud_add(self, cloud):
        body = None
        status = 200
        try:
            context = DB(user_id=self.get_ctx())
            # Sanitize
            cloud["cloud_type"] = cloud["cloud_type"].upper()
            cloud_type = cloud['cloud_type']
            if cloud_type == "AWS":
                cloud = Cloud(id=-1,
                              name=cloud['name'],
                              cloud_type=cloud['cloud_type'],
                              aws_region=cloud['aws_region'],
                              aws_key=cloud['aws_key'],
                              aws_secret_key=cloud['aws_secret_key'],
                              azure_subscription_id=None,
                              azure_tenant_id=None,
                              azure_client_id=None,
                              azure_client_secret=None)
            elif cloud_type == "AZURE":
                cloud = Cloud(id=-1,
                              name=cloud['name'],
                              cloud_type=cloud['cloud_type'],
                              aws_region=None,
                              aws_key=None,
                              aws_secret_key=None,
                              azure_subscription_id=cloud['azure_subscription_id'],
                              azure_tenant_id=cloud['azure_tenant_id'],
                              azure_client_id=cloud['azure_client_id'],
                              azure_client_secret=cloud['azure_client_secret'])
            else:
                status = 500
                body = {'message': "Unsupported cloud type"}
                return status, body
            # Add to DB
            context.add_cloud(cloud)
            if cloud.id <= 0:
                status = 500
                body = {'message': "Can't insert new cloud! Already exists?"}
                return status, body
            # Test cloud (sync)
            save_cloud_id = cloud.id
            fw = None
            if cloud.cloud_type == 'AWS':
                fw = FW_AWS(_db=context)
            if cloud.cloud_type == 'AZURE':
                fw = FW_Azure(_db=context)
            if fw != None:
                fw.save_ctx(self.get_ctx())
                if cloud.id == fw.connect(cloud.id):
                    fw.get_topology(cloud.id)
                    body = cloud.to_dict()
                else:
                    context.delete_cloud(save_cloud_id)
                    status = 500
                    body = {
                        'message': f"Can't connect to cloud: '{cloud.name}' ({cloud.cloud_type}). Bad credentials or permissions?"}
                    return status, body
        except:
            status = 500
            body = {'message': "Cloud add error"}
        return status, body

    def cloud_map(self):
        body = None
        status = 200
        try:
            db:DB = DB(self.get_ctx())
            map = CloudMap(_db=db)
            map.save_ctx(self.get_ctx())
            map.get()
            vpcs = cloud_map_encoder(map)
            inodes = InternetNodes(_db=db)
            inodes.save_ctx(self.get_ctx())
            inodes.get()
            internetNodes = internet_nodes_encoder(inodes)
            body = {
                "vpcs": vpcs,
                "inodes": internetNodes
            }
        except:
            status = 500
            body = {'message': "Get cloud-map error"}
        return status, body

    def get_vm_links(self, vm_id: int):
        body = None
        status = 200
        try:
            db:DB = DB(self.get_ctx())
            l = Links(vm_id, _db=db)
            l.save_ctx(self.get_ctx())
            l.get()
            r = VM_Rules(vm_id, _db=db)
            r.save_ctx(self.get_ctx())
            r.get()
            body = {
                "links": l.to_dict(),
                "rules": r.to_dict()
            }
        except:
            status = 500
            body = {'message': "Get VM links error"}
        return status, body

    def storages_list(self):
        clouds: list[S3_Cloud] = []
        body = None
        status = 200
        try:
            db = DB(user_id=self.get_ctx())
            for row in db.get_clouds_short():
                c = S3_Cloud(id=row[0], name=row[1], type=row[2], _db=db)
                c.save_ctx(self.get_ctx())
                c.get_buckets()
                clouds.append(c)
            body = {
                'childrenLayout': "column",
                'children': [c.to_typescript_values() for c in clouds]
            }
        except:
            status = 500
            body = {'message': "Get storages error"}
        return status, body

    def classifiers_list(self):
        body = None
        status = 200
        try:
            # here we need to load available classifiers
            c = classifier()
            body = c.get_classifiers()
        except:
            status = 500
            body = {'message': "Get classifiers error"}
        return status, body

    def classification_build2(self, sel):
        body = None
        status = 200
        try:
            # load cloud data from DB
            context = DB(user_id=self.get_ctx())
            clouds = context.get_clouds()
            map = CloudMap(_db=context)
            map.save_ctx(self.get_ctx())
            map.get()
            vpcs = map.vpcs
            sgs = get_all_rule_groups(self.get_ctx(), _db=context)
            rules = get_all_rules(self.get_ctx(), _db=context)
            nodes = Nodes(context.get_all_nodes_info())
            s = []
            for v in vpcs:
                s = s + v.subnets
            subnets = [*set(s)]
            # build classification
            c = classifier()
            c.set_selected(sel)
            sas = attr_set(c)
            if DEMO_MODE:
                sas.add_vm_info("Name", "note")
                sas.add_vm_info("<br/>Priv DNS", "privdn")
                sas.add_vm_info("<br/>Priv IP", "privip")
                sas.add_vm_info("<br/>Pub DNS", "hide_pubdn")
                sas.add_vm_info("<br/>Pub IP", "hide_pubip")
            else:
                sas.add_vm_info("Name", "note")
                sas.add_vm_info("<br/>Priv DNS", "privdn")
                sas.add_vm_info("<br/>Pub DNS", "pubdn")
                sas.add_vm_info("<br/>Pub IP", "pubip")
            vms = split_vms(clouds, vpcs, subnets,
                            nodes.nodes, sgs, rules, sas)
            t = vms.build_vms_tree(sas)
            l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
            l.make_links()
            scheme = t.dump_tree(l.ext_things)
            idl = t.get_idlist_by_node()
            links = l.dump_links(idl)
            body = {"scheme": scheme, "lines": {"items": links}}
        except:
            status = 500
            body = {'message': "Classification build error"}
        # return it to frontend
        return status, body

    def analyze_links(self):
        body = None
        status = 200
        try:
            context = DB(user_id=self.get_ctx())
            clouds = context.get_clouds()
            map = CloudMap(_db=context)
            map.save_ctx(self.get_ctx())
            map.get()
            vpcs = map.vpcs
            sgs = get_all_rule_groups(self.get_ctx(), _db=context)
            rules = get_all_rules(self.get_ctx(), _db=context)
            nodes = Nodes(context.get_all_nodes_info())
            s = []
            for v in vpcs:
                s = s + v.subnets
            subnets = [*set(s)]
            l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
            l.save_ctx(self.get_ctx())
            l.make_links()
            l.analyze_links()
            body = l.dump_analize_rezults()
        except:
            status = 500
            body = {'message': "Security analysis error"}
        # return it to frontend
        return status, body

    def analyze_results1(self):
        body = None
        status = 200
        try:
            context = DB(self.get_ctx())
            clouds = context.get_clouds()
            map = CloudMap()
            map.save_ctx(self.get_ctx())
            map.get()
            vpcs = map.vpcs
            sgs = get_all_rule_groups(self.get_ctx())
            rules = get_all_rules(self.get_ctx())
            nodes = Nodes(context.get_all_nodes_info())
            s = []
            for v in vpcs:
                s = s + v.subnets
            subnets = [*set(s)]
            l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
            l.save_ctx(self.get_ctx())
            l.make_links()
            l.analyze_links()
            body = l.issue_dump1(l.ext_things)
        except:
            status = 500
            body = {'message': "Security analysis visualisation error"}
        # return it to frontend
        return status, body

    def analyze_results2(self):
        body = None
        status = 200
        try:
            context = DB(self.get_ctx())
            clouds = context.get_clouds()
            map = CloudMap()
            map.save_ctx(self.get_ctx())
            map.get()
            vpcs = map.vpcs
            sgs = get_all_rule_groups(self.get_ctx())
            rules = get_all_rules(self.get_ctx())
            nodes = Nodes(context.get_all_nodes_info())
            s = []
            for v in vpcs:
                s = s + v.subnets
            subnets = [*set(s)]
            l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
            l.save_ctx(self.get_ctx())
            l.make_links()
            l.analyze_links()
            body = l.issue_dump2(l.ext_things)
        except:
            status = 500
            body = {'message': "Security analysis visualisation error"}
        # return it to frontend
        return status, body

    def get_header_info(self):
        db:DB = None
        body = {'message': "Get header error"}
        status = 500
        is_exist, db_current = self.__db_exist(self.get_ctx())
        if is_exist == True:
            try:
                if db_current == None:
                    db = DB(user_id=self.get_ctx())
                else:
                    db = DB(user_id=self.get_ctx(), _conn=db_current)
                clouds = db.get_clouds()
                map = CloudMap(db)
                map.save_ctx(self.get_ctx())
                map.get()
                vpcs = map.vpcs
                sgs = get_all_rule_groups(user_id=self.get_ctx(), _db=db)
                rules = get_all_rules(self.get_ctx(), _db=db)
                nodes = Nodes(db.get_all_nodes_info())
                s = []
                for v in vpcs:
                    s = s + v.subnets
                subnets = [*set(s)]
                l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
                l.save_ctx(self.get_ctx())
                l.make_links()
                l.analyze_links()
                body = {"maxSeverity": l.get_max_severity()}
                status = 200
            except:
                pass
        return status, body
