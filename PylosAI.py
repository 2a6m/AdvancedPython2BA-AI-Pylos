from lib import game
import json
import copy
import os.path
import Tree


class AI():
    '''Class representing a AI for the Pylos game.'''
    def __init__(self, tree):
        self._tree = copy.deepcopy(tree)
        self._filterList = [self.nothing, self.center, self.transfert]


    @property
    def tree(self):
        return self._tree

# -- Filters --
    def nothing(self, lst_moves):
        return lst_moves

    def center(self, lst_moves):
        center_moves = [[0, 1, 1], [0, 1, 2], [0, 2, 1], [0, 2, 2]]
        for tree in lst_moves:
            if tree.move['to'] not in center_moves:
                lst_moves.remove(tree)
        return lst_moves

    def transfert(self, lst_moves):
        for tree in lst_moves:
            if 'from' not in tree.move:
                lst_moves.remove(tree)
        return lst_moves

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
            tree = {}
            #y = Tree_Generator()
            #tree = Tree_Generator.generate_tree(state)
        return tree

    def get_next_move(self):
        return self.apply_filters(self.search_best_moves())[0].move

    def search_best_moves(self):
        tree = self._tree
        delta = self.get_delta(tree, tree.state._state['visible']['reserve'])
        #print("delta found", delta)
        best_moves = []
        for child in tree.children:
            if child.delta == delta:
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
        #print('GET DELTA EST APPLIQUEE SUR UN ARBRE AYANT ', len(tree.children), ' ENFANTS')
        if len(tree.children) == 0:
            # Case where the tree is an end-node:
            price = self.calculate_price(i_res, tree.state._state['visible']['reserve'])
            tree.set_delta(price)
            #print("feuille trouvée")
        if tree.delta != None:
            #print('delta deja existant et renvoyé')
            return tree.delta
        if tree.delta == None:
            delta = []
            for child in tree.children:
                #print('     delta du CHILD', child.delta)
                delta.append(self.get_delta(child, i_res))
                #print('     delta du TREE', tree.delta)
                #print(min(delta), max(delta), tree.state._state['visible']['turn'])
            var = [min(delta), max(delta)]
            tree.set_delta(var[tree.state._state['visible']['turn']])
            #print("TREE.DELTA", tree.delta)
            return tree.delta
