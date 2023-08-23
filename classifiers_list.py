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
                          "field": "azone`", "fn": None, "node_type": "Cloud", "node_icon": "IconInfoCircle"})

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
