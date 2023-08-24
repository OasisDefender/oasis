class vminfo:
    def __init__(self):
        self.items = []
        self.selected = []
        self.items.append({"name": "Full Host Name", "field": "name"})
        self.items.append({"name": "Private IP", "field": "privip"})
        self.items.append({"name": "Private DNS Name", "field": "privdn"})
        self.items.append({"name": "Generated Name", "field": "note"})
        self.items.append({"name": "MAC Address", "field": "mac"})
        self.items.append({"name": "Public IP", "field": "pubip"})
        self.items.append({"name": "Public DNS Name", "field": "pubdn"})

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
        self.items.append({"name": "Cloud name", "description": "Name of the cloud", "class_name": "Cloud",
                          "field": "name", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Cloud type", "description": "Type of the cloud", "class_name": "Cloud",
                          "field": "cloud_type", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Region", "description": "Region", "class_name": "Cloud",
                          "field": "aws_region", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VPC Name", "description": "VPC Name", "class_name": "VPC",
                          "field": "name", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VPC Network", "description": "VPC network", "class_name": "VPC",
                          "field": "network", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Subnet name", "description": "Subnet name", "class_name": "Subnet",
                          "field": "name", "fn": None, "node_type": "Subnet", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Subnet ARN", "description": "Subnet ARN", "class_name": "Subnet",
                          "field": "arn", "fn": None, "node_type": "Subnet", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Subnet Network", "description": "Subnet network", "class_name": "Subnet",
                          "field": "network", "fn": None, "node_type": "Subnet", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM OS", "description": "Host Operating system", "class_name": "VM",
                          "field": "os", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM State", "description": "Host current state", "class_name": "VM",
                          "field": "state", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Security group", "description": "Security group name", "class_name": "RuleGroup",
                          "field": "name", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "Availability Zone", "description": "VM Availability Zone", "class_name": "VM",
                          "field": "azone", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Functional Type", "description": "Functional type based on security rules", "class_name": "Rule",
                          "field": " ", "fn": "server_type", "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Public IP", "description": "Interface Public Address", "class_name": "VM",
                          "field": "pubip", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Private IP", "description": "Interface Private Address", "class_name": "VM",
                          "field": "privip", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Private DNS Name", "description": "Private DNS Name", "class_name": "VM",
                          "field": "privdn", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Name", "description": "Host Name", "class_name": "VM",
                          "field": "name", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})
        self.items.append({"name": "VM Description", "description": "Host description", "class_name": "VM",
                          "field": "note", "fn": None, "node_type": "VPC", "node_icon": "IconInfoCircle"})

    def add(self, name, description, class_name, field, fn=None, node_type="Cloud", node_icon="IconInfoCircle"):
        self.item = {}
        self.item["name"] = name
        self.item["description"] = description
        self.item["class_name"] = class_name
        self.item["field"] = field
        self.item["fn"] = fn
        self.item["node_type"] = node_type
        self.item["node_icon"] = node_icon
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
