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

    def board_remove(self, state):
        '''
        travel the board and save all the marbles that can be removed

        :return: list of removable marbles
        '''
        board = list()
        for layer in range(4):
            for row in range(4-layer):
                for column in range(4-layer):
                    try:
                        state.remove((layer, row, column), 0)
                        # self._player or self._playernb
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
        for pos in self.board_free(state):
            price = 1
            child_state = pyl.PylosState(state)
            move = {'move': 'place', 'to': list(pos)}
            child_state.update(move, 0)
            if child_state.createSquare(pos):
                for combi in self.square_remove(child_state):
                    move['remove'] = combi
                    child_state.update(move, 0)
                    price -= len(combi)
                    tree.addChild(Tree.Tree(child_state, move, price))
            else:
                tree.addChild(Tree.Tree(child_state, move, price))

    def generate_from_remove(self, tree, state):
        # Case where the AI deplaces an existing marble
        for pos in self.board_remove(state):
            price = 0
            child_state1 = pyl.PylosState(state)
            transitory_state = pyl.PylosState(child_state1)
            move = {'move': 'move', 'from': list(pos)}
            transitory_state.remove(pos, 0)
            for upperpos in self.board_free(transitory_state):
                child_state2 = pyl.PylosState(child_state1)
                if upperpos[0] > pos[0]:
                    move['to'] = list(upperpos)
                    print(upperpos)
                    child_state2.update(move,0)
                    if child_state2.createSquare(pos):
                        for combi in self.square_remove(child_state2):
                            move['remove'] = combi
                            child_state2.update(move, 0)
                            price -= len(combi)
                            tree.addChild(Tree.Tree(child_state2, move, price))
                    else:
                        tree.addChild(Tree.Tree(child_state2, move, price))

    def generate_tree(self, state):
        t0 = Tree.Tree(state, 0, [])
        self.generate_from_free(t0, state)
        self.generate_from_remove(t0, state)
        t0.saveTree("TEST")
        print("arbre généré")

test = Tree_Generator()
test.generate_tree(pyl.PylosState())
