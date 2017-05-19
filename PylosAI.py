from lib import game
import json
import copy
import os.path
import Tree
import Tree_Generator as treegen

class AI():
    '''Class representing a AI for the Pylos game.'''
    def __init__(self, state, player):
        self._moves = {}
        # Forme du dico ?? {'move':price, 'move':price}
        # Dico ou liste ?? meilleur pour un arbre ??
        self.__origin_state = state
        self.__player = player
        self._tree_generator = treegen.Tree_Generator()


    @property
    def player(self):
        return self.__player

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

    def extract_state_from_tree_list(self, tree_list):
        '''
        :param tree_list:
        :return: (type = list of "PylosState" object)
        '''
        ans = []
        for tree in tree_list:
            ans.append(copy.deepcopy(tree.state))
        return ans
