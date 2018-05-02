from collections import deque
from typing import Iterable

class HTMLNode(object):
    def __init__(self, nodeName: str):
        self.name = nodeName
        self.childList = deque()
        self.attributes = dict()

    def getElementsByTagNames(self, names: Iterable) -> set:
        result = set()
        if self.name in names:
            result.add(self)
        for n in self.childList:
            result.update(n.getElementsByTagNames(names))
        return result
    
    def __repr__(self):
        return (self.name + ", attributes: " + str(self.attributes)
            + ", number of children: " + len(self.childList))
