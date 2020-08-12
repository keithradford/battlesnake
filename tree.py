class Node:

    def __init__(self, coords):
        self.children = []
        self.coords = coords

    def getCoords(self):
        return self.coords

    def getX(self):
        return self.coords['x']

    def getY(self):
        return self.coords['y']

    def getChildren(self):
        return self.children

    def addChild(self, child):
        if isinstance(child, dict):
            if 'x' in dict.keys() and 'y' in dict.keys():
                self.children.append(child)
        else:
            print(f'Child {child} trying to add not valid formatting')
