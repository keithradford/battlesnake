# class Node:

#     def __init__(self, data):

#         self.left = None
#         self.right = None
#         self.data = data


#     def PrintTree(self):
#         print(self.data)

class Node:

    def __init__(self):
        self.children = []
        self.coords = None #To do: Change this to match coords in response