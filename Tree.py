import copy
import json


class Tree():
    def __init__(self, state, delta=None, move=None, children=[]):
        self.__value = [state, move, delta]
        self.__children = copy.copy(children)

    def __getitem__(self, index):
        return self.__children[index]

    def __str__(self):
        def _str(tree, level):
            result = '[{}]\n'.format(tree.__value)
            for child in tree.children:
                result += '{} |--{}'.format('   ' * level, _str(child, level + 1))
            return result
        return _str(self, 0)

    @property
    def state(self):
        return self.__value[0]

    @property
    def move(self):
        return self.__value[1]
    @property
    def delta(self):
        return self.__value[2]

    @property
    def children(self):
        return copy.copy(self.__children)

    @property
    def size(self):
        result = 1
        for child in self.__children:
            result += child.size
        return result

    def set_delta(self, delta):
        self.__value[2] = delta


    def addChild(self, tree):
        '''
        add a child to the node

        :param tree: tree object
        :return:
        '''
        self.__children.append(tree)
        return

    def endTree(self):
        '''
        find all the child at th end of the tree

        :return: list of end child
        '''
        children = []
        if len(self.children) == 0:
            return self
        else:
            for child in self.children:
                print('HELP', type(child.state))
                children += [child.endTree()]
        return children
