from flask import jsonify
import json

from ctx import CTX  # base class for frontend objects
from cloud import Cloud
from db import DB
from cloud_map import CloudMap, cloud_map_encoder
from internet_nodes import InternetNodes, internet_nodes_encoder
from links import Links, link_encoder
from fw_aws import FW_AWS
from fw_azure import FW_Azure
from fw import FW_Selected, FW_Selected_encoder
from vm_rules import VM_Rules
from s3_bucket import S3_Bucket, S3_Cloud
from classifiers_list import classifier
from split_vms import attr_set, split_vms
from rule_group import RuleGroup, get_all_rule_groups
from rule import Rule, get_all_rules
from vm import Nodes
from links_by_rules import links_by_rules
from global_settings import DEMO_MODE

class Backend(CTX):
    def __init__(self):
        pass


    def get_clouds(self):
        db = DB(self.get_ctx())
        clouds = db.get_clouds()
        return [c.to_dict() for c in clouds]


    def cloud_sync(self, id: int):
        fw = None
        context = DB(self.get_ctx())
        retmsg = ""
        retval = 200
        cloud: Cloud = None

        for cloud in context.get_clouds():
            if cloud.id == id:
                if cloud.cloud_type == 'AWS':
                    fw = FW_AWS()
                    break
                if cloud.cloud_type == 'AZURE':
                    fw = FW_Azure()
                    break
                retmsg = f"Cloud Type: '{cloud.cloud_type}' - not supported!"
                retval = 500
        if fw != None:
            fw.save_ctx(self.get_ctx())
            context.sync_cloud(cloud.id)
            fw.connect(cloud.id)
            fw.get_topology(cloud.id)
        return retmsg, retval


    def cloud_delete(self, id: int):
        db = DB(self.user_id)
        db.delete_cloud(id)
        return "", 200


    def get_header_info(self):
        db = DB(self.get_ctx())
        clouds = db.get_clouds()
        map = CloudMap()
        map.save_ctx(self.get_ctx())
        map.get()
        vpcs = map.vpcs

        sgs = get_all_rule_groups(self.get_ctx())
        rules = get_all_rules(self.get_ctx())
        nodes = Nodes(db.get_all_nodes_info())
        s = []
        for v in vpcs:
            s = s + v.subnets
        subnets = [*set(s)]

        l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
        l.save_ctx(self.get_ctx())
        l.make_links()
        l.analyze_links()
        res = l.get_max_severity()

        return jsonify({"maxSeverity": res})

    def cloud_add(self, reqCloud: str):
        context = DB(self.get_ctx())
        # Sanitize
        reqCloud["cloud_type"] = reqCloud["cloud_type"].upper()
        cloud_type = reqCloud['cloud_type']
        if cloud_type == "AWS":
            cloud = Cloud(id=-1,
                        name=reqCloud['name'],
                        cloud_type=reqCloud['cloud_type'],
                        aws_region=reqCloud['aws_region'],
                        aws_key=reqCloud['aws_key'],
                        aws_secret_key=reqCloud['aws_secret_key'],
                        azure_subscription_id=None,
                        azure_tenant_id=None,
                        azure_client_id=None,
                        azure_client_secret=None)
        elif cloud_type == "AZURE":
            cloud = Cloud(id=-1,
                        name=reqCloud['name'],
                        cloud_type=reqCloud['cloud_type'],
                        aws_region=None,
                        aws_key=None,
                        aws_secret_key=None,
                        azure_subscription_id=reqCloud['azure_subscription_id'],
                        azure_tenant_id=reqCloud['azure_tenant_id'],
                        azure_client_id=reqCloud['azure_client_id'],
                        azure_client_secret=reqCloud['azure_client_secret'])
        else:
            return "Unsupported cloud type", 500

        # Add to DB
        context.add_cloud(cloud)
        if cloud.id <= 0:
            return "Can't insert new cloud! Already exists?", 500

        # Test cloud
        save_cloud_id = cloud.id
        fw = None
        if cloud.cloud_type == 'AWS':
            fw = FW_AWS()
        if cloud.cloud_type == 'AZURE':
            fw = FW_Azure()
        if fw != None:
            fw.save_ctx(self.get_ctx())
            if cloud.id == fw.connect(cloud.id):
                fw.get_topology(cloud.id)
            else:
                context.delete_cloud(save_cloud_id)
                return f"Can't connect to cloud: '{cloud.name}' ({cloud.cloud_type}). Bad credentials or permissions?", 500

        return cloud.to_dict(), 200


    def cloud_map(self):
        map = CloudMap()
        map.save_ctx(self.get_ctx())
        map.get()
        vpcs = cloud_map_encoder(map)

        inodes = InternetNodes()
        inodes.save_ctx(self.get_ctx())
        inodes.get()
        internetNodes = internet_nodes_encoder(inodes)

        result = {
            "vpcs": vpcs,
            "inodes": internetNodes
        }

        return json.dumps(result, ensure_ascii=False), 200


    def get_vm_links(self, vm_id: int):
        l = Links(vm_id)
        l.save_ctx(self.get_ctx())
        l.get()
        lines = json.dumps(l, default=link_encoder, ensure_ascii=False)
        r = VM_Rules(vm_id)
        r.save_ctx(self.get_ctx())
        r.get()
        rules = json.dumps(r.to_dict())
        reply = f"{{\"links\": {lines}, \"rules\": {rules}}}"
        return reply


    def storages_list(self):
        clouds: list[S3_Cloud] = []
        db = DB(self.get_ctx())
        for row in db.get_clouds_short():
            c = S3_Cloud(id=row[0], name=row[1], type=row[2])
            c.save_ctx(self.get_ctx())
            c.get_buckets()
            clouds.append(c)
        retval = {
            'childrenLayout': "column",
            'children': [c.to_typescript_values() for c in clouds]
        }
        return jsonify(retval)


    def classifiers_list(self):
        # here we need to load available classifiers
        c = classifier()
        return jsonify(c.get_classifiers())


    def classification_build(self, sel):
        # load cloud data from DB
        context = DB(self.get_ctx())
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

        # build classification
        c = classifier()
        c.set_selected(sel)
        sas = attr_set(c)

        sas.add_vm_info("Name", "note")
        sas.add_vm_info("<br/>Priv DNS", "privdn")
        sas.add_vm_info("<br/>Pub DNS", "pubdn")
        sas.add_vm_info("<br/>Pub IP", "pubip")

        vms = split_vms(clouds, vpcs, subnets, nodes.nodes, sgs, rules, sas)
        t = vms.build_vms_tree(sas)
        res = t.dump_tree()

        # return it to frontend
        return jsonify(res)


    def classification_build2(self, sel):
        # load cloud data from DB
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

        vms = split_vms(clouds, vpcs, subnets, nodes.nodes, sgs, rules, sas)
        t = vms.build_vms_tree(sas)
        l = links_by_rules(clouds, nodes.nodes, subnets, sgs, rules)
        l.make_links()
        scheme = t.dump_tree(l.ext_things)
        idl = t.get_idlist_by_node()
        links = l.dump_links(idl)
        res = {"scheme": scheme, "lines": {"items": links}}

        # return it to frontend
        return jsonify(res)


    def analyze_links(self):
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
        ar = l.dump_analize_rezults()
        return jsonify(ar)
