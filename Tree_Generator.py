from lib import game
import json
import copy
import Tree
import pylos as pyl

class Tree_Generator():
    '''Creates the Tree chart for PylosAI'''
    def __init__(self):
        pass

    """

    def save_place_upperlayer(self, state, pos):
        return

    def save_move_upperlayer(self, state, pos):
        for balls in self.board_remove():
            if balls[0] == int((pos[0])-1):
                price = 0
                move = {'move': 'move', 'from': list(balls), 'to': list(pos)}
        return move

    def save_place_square_r1(self, place):
        if self._state.createSquare(place):
            if len(self.board_remove()) == 1:
                price = 0
                move = {'move': 'place', 'to': list(place), 'remove': self.board_remove()[0]}
                self._moves[json.dumps(move)] = (place, price)
        return

    def save_place_square_r2(self, place):
        if self._state.createSquare(place):
            if len(self.board_remove()) == 2:
                price = -1
                # AI doit chercher quelles billes il va retirer
                move = {'move': 'place', 'to': list(place), 'remove': [self.board_remove()[0], self.board_remove()[1]]}
                self._moves[json.dumps(move)] = (place, price)
        return

    def save_move_square_r1(self, place):
        if self._state.createSquare(place):
            if len(self.board_remove()) == 2:
                price = -1
                # AI doit chercher quelles billes il va retirer
                move = {'move': 'move', 'from': self.board_remove()[0], 'to': list(place), 'remove': [self.board_remove()[1], self.board_remove()[2]]}
                self._moves[json.dumps(move)] = (place, price)
        return

    def save_move_square_r2(self, place):
        if self._state.createSquare(place):
            if len(self.board_remove()) == 3:
                price = -2
                # AI doit chercher quelles billes il va retirer
                move = {'move': 'move', 'from': self.board_remove()[0], 'to': list(place), 'remove': [self.board_remove()[1], self.board_remove()[2]]}
                self._moves[json.dumps(move)] = (place, price)
        return

    def save_place(self, pos):
        price = 1
        move = {'move': 'place', 'to': list(pos)}
        return (price, move)

    """


    def board_free(self, state):
        '''
        travel the board and save all the free positions in a list

        :return: the list of the free positions
        '''
        board = list()
        for layer in range(4):
            for row in range(4-layer):
                for column in range(4-layer):
                    try:
                        state.validPosition(layer, row, column)
                        if state.get(layer, row, column) is None:
                            board.append((layer, row, column))
                    except:
                        pass
        return board

    def board_remove(self, state, player):
        '''
        travel the board and save all the marbles that can be removed
        :return: list of removable marbles
        '''
        board = list()
        for layer in range(4):
            for row in range(4 - layer):
                for column in range(4 - layer):
                    try:
                        state.canMove(layer, row, column)
                        sphere = state.get(layer, row, column)
                        if sphere != player:
                            raise game.InvalidMoveException('not your sphere')
                        board.append((layer, row, column))
                    except:
                        pass
        return board

    def square_remove(self, state):
        """
        :param state:
        :return: List of all the possible combinations of marbles the AI can remove after it has created a square
        """
        data = self.board_remove(state)
        ans = []
        for i in range(len(data)):
            combi = [data[i]]
            for j in range(i, len(data)):
                combi.append(data[j])
            ans.append(tuple(combi))
        return ans

    def generate_from_free(self, tree, state):
        # Case where the AI places a marble
        children = []
        for pos in self.board_free(state):
            price = 1
            child_state1 = copy.deepcopy(pyl.PylosState(state._state['visible']))
            move = {'move': 'place', 'to': list(pos)}
            child_state1.update(move, state._state['visible']['turn'])
            if child_state1.createSquare(pos):
                combi = self.board_remove(child_state1, state._state['visible']['turn'])
                child_state2 = copy.deepcopy(pyl.PylosState(state._state['visible']))
                if len(combi) >= 2:
                    move['remove'] = [combi[0], combi[1]]
                else:
                    move['remove'] = combi
                child_state2.update(move, child_state2._state['visible']['turn'])
                price -= len(combi)
                children.append(Tree.Tree(child_state2, price, move))
            else:
                child_state = copy.deepcopy(pyl.PylosState(state._state['visible']))
                child_state.update(move, child_state._state['visible']['turn'])
                children.append(Tree.Tree(child_state, price, move))
        return children

    def generate_from_remove(self, tree, state):
        # Case where the AI deplaces an existing marble
        children = []
        for pos in self.board_remove(state, state._state['visible']['turn']):
            price = 0
            child_state1 = copy.deepcopy(pyl.PylosState(state._state['visible']))
            transitory_state = copy.deepcopy(pyl.PylosState(state._state['visible']))
            move = {'move': 'move', 'from': list(pos)}
            transitory_state.remove(pos, child_state1._state['visible']['turn'])
            for upperpos in self.board_free(transitory_state):
                child_state2 = copy.deepcopy(pyl.PylosState(child_state1._state['visible']))
                if upperpos[0] > pos[0]:
                    move['to'] = list(upperpos)
                    child_state2.update(move, child_state2._state['visible']['turn'])
                    if child_state2.createSquare(pos):
                        combi = self.board_remove(child_state1, state._state['visible']['turn'])
                        child_state3 = copy.deepcopy(pyl.PylosState(state._state['visible']))
                        if len(combi) >= 2:
                            move['remove'] = [combi[0], combi[1]]
                        else:
                            move['remove'] = combi
                        child_state3.update(move, child_state3._state['visible']['turn'])
                        price -= len(combi)
                        children.append(Tree.Tree(child_state3, price, move))
                    else:
                        children.append(Tree.Tree(child_state2, price, move))
        return children

# test symetry

    def rot(self, matrix):
        for i in range(len(matrix)):
            for j in range(i):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        return matrix

    def axisY(self, matrix):
        for i in range(len(matrix)):
            matrix[i].reverse()
        return matrix

    def axisX(self, matrix):
        matrix.reverse()
        return matrix

    def noSymetry(self, matrix1, matrix2):
        if matrix1 == self.rot(copy.deepcopy(matrix2)) or \
                        matrix1 == self.rot(self.rot(copy.deepcopy(matrix2))) or \
                        matrix1 == self.rot(self.rot(self.rot(copy.deepcopy(matrix2)))) or \
                        matrix1 == self.axisY(copy.deepcopy(matrix2)) or \
                        matrix1 == self.axisX(copy.deepcopy(matrix2)) or \
                        matrix1 == self.axisX(self.axisY(copy.deepcopy(matrix2))):
            raise EnvironmentError

# Generate a Tree
    def start(self, state):
        t0 = Tree.Tree(state, 0, [])
        self.generate_tree(t0)
        t0.saveTree("TEST.json")
        print('arbre sauvé')

    def generate_tree(self, tree, it=0, gen=0):
        # children = self.generate_from_free(tree, tree.state)
        children = self.generate_from_free(tree, tree.state) + self.generate_from_remove(tree, tree.state)
        if it >= 4:# mettre 4 poir le 1er tour mais 3 pour la suite du jeu
            pass
        else:
            it += 1
            for child in children:
                if len(tree.children) == 0:
                    gen += 1
                    tree.addChild(child)
                    self.generate_tree(child, it, gen)
                else:
                    try:
                        for ch in tree.children:
                            m1 = child.state._state['visible']['board'][0]
                            m2 = ch.state._state['visible']['board'][0]
                            self.noSymetry(m1, m2)
                        gen += 1
                        tree.addChild(child)
                        self.generate_tree(child, it, gen)
                    except:
                        # print('symetry')
                        pass

        #print("t0f = ", tree)
        #print(it, gen, sep=' : ')
        return

    def loadTree(self, file):
        with open(file) as f:
            tree = Tree.dico2t(json.load(f))
        return tree

# TEST FIELD

test = Tree_Generator()
state_test = pyl.PylosState({'board': [[[1, 1, 1, 1], [1, None, None, 1], [0, None, None, 0],[0, 0, 0, 0]],
                                       [[None, None, None], [None, None, None],[None, None, None]],
                                       [[None, None],[None, None]],
                                       [[None]]],'reserve': [9, 9],'turn': 0})
test.start(state_test)

'''
print(state_test)
tree = test.loadTree('TEST.json')
print('tree loaded')
a = tree.find(state_test)
if len(a) == 1:
    tree = a[0]
    print(tree.endTree())
    for end in tree.endTree():
        for e in end:
            print(e)
            print('type state', type(e.state))
            print('type', type(e))
            test.generate_tree(e)
    tree.saveTree('TEST3,5.json')
    print('tree saved')
else:
    tree = Tree.Tree(state_test,
                     state_test._state['visible']['reserve'][0] - state_test._state['visible']['reserve'][1], [])
    test.generate_tree(tree)
tree.saveTree('TEST3,5.json')


tree = test.loadTree('Test 3,5.json')
a = tree.find(state_test)
print(a)
'''

'''
        t = tree
        # il ne fait qu'un seul branchage
        if len(t.children) == 0:
            return
        else:
            for child in t.children:
                print(child.state)
                print(type(child.state))
                children = self.generate_from_free(child, child.state)
                # self.generate_from_remove(child, child.state)
                for ch in children:
                    tree.addChild(ch)
                    self.generate_tree(ch)
            # il ne fait qu'un seul branchage
'''