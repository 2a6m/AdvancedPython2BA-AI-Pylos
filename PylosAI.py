from lib import game
import json
import copy
import os.path
import Tree

class AI():
    '''Class representing a AI for the Pylos game.'''
    def __init__(self, state, player):
        self._moves = {}
        # Forme du dico ?? {'move':price, 'move':price}
        # Dico ou liste ?? meilleur pour un arbre ??
        self.__origin_state = state
        self.__player = player
        self._filterList = [self.nothing, self.center, self.transfert]


    @property
    def player(self):
        return self.__player

# -- Filters --
    def nothing(self, lst_moves):
        return

    def center(self, lst_moves):
        center_moves = [[0, 1, 1], [0, 1, 2], [0, 2, 1], [0, 2, 2]]
        for tree in lst_moves:
            if tree.move['to'] not in center_moves:
                del lst_moves[tree]

    def transfert(self, lst_moves):
        for tree in lst_moves:
            if 'from' not in tree.move:
                del lst_moves[tree]

# --  --
    def loadTree(self, state):
        '''
        look if there is a tree or a tree update

        :return: first, tree update; second, tree of the all game
        '''
        tree_file = 'TEST.json'
        game_tree_file = 'GAME_TREE.json'
        if os.path.isfile(game_tree_file):
            tree = Tree.dico2t(game_tree_file)
        elif os.path.isfile(tree_file):
            tree = Tree.dico2t(json.load(tree_file))
        else:
            print('THERE IS NO GAME TREE')
            tree = {}
            #y = Tree_Generator()
            #tree = Tree_Generator.generate_tree(state)
        return tree

    def search_best_moves(self, state):
        tree = self.loadTree(state)
        delta = self.get_delta(tree, state._state['visible']['reserve'])
        best_moves = []
        for child in tree.children:
            if child.delta == tree.delta:
                best_moves.append(child)
                #It isn't necessary to deepcopy the whole tree as we don't need its children anymore
        return best_moves

    def apply_filters(self, best_moves):
        """ATTENTION: IL FAUT ENCORE CREER UN ATTRIBUT ET DES FILTRES A LA CLASS AFIN QUE CETTE FONCTION SOIT COMPLETE"""
        filtered_moves = best_moves
        i = 0
        while len(filtered_moves) > 1 and i < len(self._filterList):
            filtered_moves = self._filterList[i](filtered_moves)
            i += 1
        if len(filtered_moves) == 0:    # sécu si les filtres sont trop bourrins
            return best_moves[0]
        return filtered_moves

    def calculate_price(self, i_res, f_res):
        #The price is the number of marbles the first player placed mius the number of marbles the second player placed
        return i_res[0] - f_res[0] - i_res[1] + f_res[1]

    def get_delta(self, tree, i_res):
        '''

        :param tree:
        :param i_res: Initial reserve the function has to use in order to calculate the price from a reference point
        :return: value of difference of marbles between the first and second player. The value is positiv if the first
        player has the upper hand.
        '''
        if len(tree.children) == 0:
            # Case where the tree is an end-node:
            price = self.calculate_price(i_res, tree.state._state['visible']['reserve'])
            tree.delta = price
        if tree.delta != None:
            return tree.delta
        if tree.delta == None:
            delta = []
            for child in tree.children:
                delta.append(self.get_delta(child, i_res))
            tree.delta = [min(delta), max(delta)][tree.state._state['visible']['turn']]
            return tree.delta

    """
    def scan_for_best_move(self, tree):
        '''
        Scan trough the given tree and evaluates de cost at each terminal move as the enemy always plays
        the best one for him.
        :param tree:
        :return: list of the best possible move of equivalent price the AI can play from the given tree (type = list of
        "Tree" objects)
        '''
        reserve = tree.state._state['visible']['reserve']
        turn = tree.state._state['visible']['turn']
        best_price = -2
        best_move = []
        for case in self.get_latest_children(tree):
            score = reserve[turn] - case.state._state['visible']['reserve'][turn] - reserve[(turn+1)%2] + \
            case.state._state['visible']['reserve'][(turn+1)%2]
            if score > best_price:
                best_price = score
                best_move = [copy.deepcopy(case)]
            elif score == best_price:
                best_move.append[copy.deepcopy(case)]
        print("Best_move price is: ", best_price)
        return best_move

    def get_latest_children(self, tree):
        '''
        :param tree:
        :return: list of all the last child_tree's generated from the tree in parameter (type = list of "Tree" objects)
        NOTE: This function should rather be included in the "Tree" module...
        '''
        ans = []
        for child_tree in tree.children:
            if len(child_tree.children) == 0:
                ans.append(copy.deepcopy(child_tree))
            else:
                ans + self.get_latest_children(child_tree)
        return ans

    def choose(self, matrix):
        '''
        Look at the end of the trees and calculated the percentage of victory

        :param matrix:
        :return: choose the move with best percentage
        '''
        mean = []
        for i in matrix:
            for j in matrix:
                m_elem = (matrix[i][j].endState(self.player), matrix[i][j]['move'], matrix[i][j])
                mean.append(m_elem)
        value = 0
        move = ''
        tree = {}
        for elem in mean:
            if elem[0] > value:
                value = elem[0]
                move = elem[1]
                tree = elem[2]
        tree.saveTree('GAME_TREE.json')
        return move

    def search(self, state):
        tree = self.loadTree(state)
        possibilities = tree.find(state)
        return self.choose(possibilities)

    """