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
        self.items.append({"name": "Cloud", "description": "split by clouds", "class_name": "Cloud",
                          "field": "name", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": [{"title": "Type", "attr": "cloud_type", "icon": "IconInfoCircle"}, {"title": "Region", "attr": "aws_region", "icon": "IconInfoCircle"}]})
        self.items.append({"name": "Cloud type", "description": "split by cloud type", "class_name": "Cloud",
                          "field": "cloud_type", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Region", "description": "Region", "class_name": "Cloud",
                          "field": "aws_region", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VPC", "description": "Split by VPC/VNet", "class_name": "VPC",
                          "field": "name", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle", "info": [{"title": "Net Address", "attr": "network"}]})
        self.items.append({"name": "Subnet", "description": "Subnet name", "class_name": "Subnet",
                          "field": "name", "fn": None, "node_type": "Subnet", "node_icon": "IconInfoCircle", "info": [{"title": "ARN", "attr": "arn"}, {"title": "Address", "attr": "network"}]})
        self.items.append({"name": "VM OS", "description": "Host Operating system", "class_name": "OneNode",
                          "field": "os", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM State", "description": "Host current state", "class_name": "OneNode",
                          "field": "state", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Security group", "description": "Security group name", "class_name": "RuleGroup",
                          "field": "name", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "Availability Zone", "description": "VM Availability Zone", "class_name": "OneNode",
                          "field": "azone", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Functional Type", "description": "Functional type based on security rules", "class_name": "Rule",
                          "field": " ", "fn": "server_type", "node_type": "VPC", "node_icon": "IconInfoCircle", "info": []})
        self.items.append({"name": "VM Public IP", "description": "Interface Public Address", "class_name": "OneNode",
                          "field": "pubip", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Private IP", "description": "Interface Private Address", "class_name": "OneNode",
                          "field": "privip", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Private DNS Name", "description": "Private DNS Name", "class_name": "OneNode",
                          "field": "privdn", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Name", "description": "Host Name", "class_name": "OneNode",
                          "field": "name", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        '''        self.items.append({"name": "VM", "description": "Host description", "class_name": "OneNode",
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
        self.items.append({"name": "VM Type", "description": "Host type", "class_name": "OneNode",
                          "field": "type", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})

    def add(self, name, description, class_name, field, fn=None, node_type="Cloud", node_icon="IconInfoCircle", info=[]):
        self.item = {}
        self.item["name"] = name
        self.item["description"] = description
        self.item["class_name"] = class_name
        self.item["field"] = field
        self.item["fn"] = fn
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
