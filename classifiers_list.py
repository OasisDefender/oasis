class classifier:
    def __init__(self):
        self.items = []
        self.selected = []

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
