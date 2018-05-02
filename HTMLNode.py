
class HTMLNode(object):
    def __init__(self, nodeName):
        self.name = nodeName
        self.childList = []
        self.attributes = dict()
        self.parent = None

    def appendChild(self, node):
        self.childList.append(node)
        node.parent = self
    
    def getElementsByName(self, name):
        result = set()
        if self.name == name:
            result.add(self)
        for n in self.childList:
            result.update(n.getElementsByName(name))
        return result
    
    def __repr__(self):
        return (self.name + ", attributes: " + str(self.attributes)
            + ", number of children: " + len(self.childList))
