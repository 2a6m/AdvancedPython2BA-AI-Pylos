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

    def find(self, state, lst=[]):
        '''
        search a particuliar node (from the state) in the tree

        :param state:
        :param lst:
        :return: the tree of the nodes in list
        '''
        if self.state == state._state['visible']:
            lst.append(self.children)
        for child in self.children:
            lst.append(child.find(state))
        return lst

    def endTree(self):
        children = []
        if len(self.children) == 0:
            return self
        else:
            for child in self.children:
                print('HELP', type(child.state))
                children += [child.endTree()]
        return children

    def endState(self, player):
        '''
        calculate the percentage of winning at the end of the tree

        :param player:
        :return: percentage
        '''
        tot = 0
        if len(self.children) == 0:
            if self.state['state']['board'][3][1][1] == player:
                return 1
            else:
                return 0
        else:
            for child in self.children:
                tot += child.endState(player)
        return tot / len(self.children)

def dico2t(dico):
    return Tree(dico['state'], dico['move'], dico['delta'], [dico2t(children) for children in dico['children']])

