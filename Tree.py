import copy
import json


class Tree():
    def __init__(self, state, delta, move, children=[]):
        self.__value = (state, move, delta)
        self.__children = copy.deepcopy(children)

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
        return copy.deepcopy(self.__children)

    @property
    def size(self):
        result = 1
        for child in self.__children:
            result += child.size
        return result

    def t2dico(self):
        dico = dict()
        dico['state'] = self.state._state['visible']
        dico['move'] = self.move
        dico['delta'] = self.delta
        dico['children'] = [children.t2dico() for children in self.children]
        return dico

    def saveTree(self, file):
        data = self.t2dico()
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    def addChild(self, tree):
        self.__children.append(tree)
        return


def dico2t(dico):
    return Tree(dico['state'], dico['move'], dico['delta'], [dico2t(children) for children in dico['children']])

