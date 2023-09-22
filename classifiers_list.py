class vminfo:
    def __init__(self):
        self.items = []
        self.selected = []
        self.items.append({"name": "Full Host Name", "field": "name"})
        self.items.append({"name": "Private IP", "field": "privip"})
        self.items.append({"name": "Private DNS Name", "field": "privdn"})
        self.items.append({"name": "Public IP", "field": "pubip"})
        self.items.append({"name": "Public DNS Name", "field": "pubdn"})
        self.items.append({"name": "Generated Name", "field": "note"})
        self.items.append({"name": "MAC Address", "field": "mac"})
        self.items.append({"name": "OS", "field": "os"})
        self.items.append({"name": "State", "field": "state"})

    def get_info(self):
        res = []
        for idx in range(0, len(self.items)):
            item = {"id": idx, "name": self.items[idx]["name"]}
            res.append(item)
        return res

    def set_selected(self, selected: list[int]):
        self.selected = []
        for i in selected:
            self.selected.append(self.items[i])


class classifier:
    def __init__(self):
        self.items = []
        self.selected = []
        self.items.append({"name": "Cloud", "description": "Group by cloud instance", "class_name": "Cloud",
                          "field": "name", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": [{"title": "Type", "attr": "cloud_type", "icon": "IconInfoCircle"}, {"title": "Region", "attr": "aws_region", "icon": "IconInfoCircle"}]})
        self.items.append({"name": "Cloud type", "description": "Group by cloud type (AWS, AZURE, etc..)", "class_name": "Cloud",
                          "field": "cloud_type", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Region", "description": "Group by cloud region", "class_name": "Cloud",
                          "field": "aws_region", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VPC", "description": "Group by VPC/VNet", "class_name": "VPC",
                          "field": "name", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": [{"title": "Net Address", "attr": "network"}]})
        self.items.append({"name": "Subnet", "description": "Group by subnet", "class_name": "Subnet",
                          "field": "name", "node_type": "Subnet", "node_icon": "IconInfoCircle", "info": [{"title": "ARN", "attr": "arn"}, {"title": "Address", "attr": "network"}]})
        self.items.append({"name": "VM OS", "description": "Group by host Base Software", "class_name": "OneNode",
                          "field": "os", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM State", "description": "Group by host current state", "class_name": "OneNode",
                          "field": "state", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Security group", "description": "Group by security group", "class_name": "RuleGroup",
                          "field": "name", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Availability Zone", "description": "Group by host Availability Zone", "class_name": "OneNode",
                          "field": "azone", "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Functional Type (detailed)", "description": "Group by provided services (one group - one port), based on security rules", "class_name": "Rule",
                          "field": "server_type", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Functional Type (aggregated)", "description": "Group by provided services (one group - one port range), based on security rules", "class_name": "Rule",
                          "field": "server_type1", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Rule direction", "description": "Group by security rule direction (ingress/egress)", "class_name": "Rule",
                          "field": "rule_direction", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Rule proto", "description": "Group by security rule protocol", "class_name": "Rule",
                          "field": "proto", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        '''
        self.items.append({"name": "VM Public IP", "description": "Group by Interface Public Address", "class_name": "OneNode",
                          "field": "pubip", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Private IP", "description": "Interface Private Address", "class_name": "OneNode",
                          "field": "privip", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Private DNS Name", "description": "Private DNS Name", "class_name": "OneNode",
                          "field": "privdn", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Name", "description": "Host Name", "class_name": "OneNode",
                          "field": "name", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM", "description": "Host description", "class_name": "OneNode",
                          "field": "note", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle",
                           "info": [
                               {"title": "Software", "attr": "os"},
                               {"title": "State", "attr": "state"},
                               {"title": "Public DNS", "attr": "pubdn"},
                               {"title": "Private DNS", "attr": "privdn"},
                               {"title": "Public IP", "attr": "pubip"},
                               {"title": "Private IP", "attr": "privip"},
                               {"title": "Name", "attr": "name"}
                           ]})
        '''
        self.items.append({"name": "VM Type", "description": "Group by host type", "class_name": "OneNode",
                          "field": "type", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "RuleAddr", "description": "Group by target address in security rule", "class_name": "Rule",
                          "field": "naddr", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})

    def add(self, name, description, class_name, field, fn=None, node_type="Cloud", node_icon="IconInfoCircle", info=[]):
        self.item = {}
        self.item["name"] = name
        self.item["description"] = description
        self.item["class_name"] = class_name
        self.item["field"] = field
        self.item["node_type"] = node_type
        self.item["node_icon"] = node_icon
        self.item["info"] = info
        self.items.append(self.item)

    def get_classifiers(self):
        res = []
        for idx in range(0, len(self.items)):
            item = {"id": idx, "name": self.items[idx]["name"],
                    "description": self.items[idx]["description"]}
            res.append(item)
        return res

    def set_selected(self, selected: list[int]):
        self.selected = []
        for i in selected:
            self.selected.append(self.items[i])
