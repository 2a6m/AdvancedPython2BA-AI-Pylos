from lib import game
import json
import copy

class AI():
    '''Class representing a AI for the Pylos game.'''
    def __init__(self, state, player):
        self._moves = {}
        # Forme du dico ?? {'move':price, 'move':price}
        # Dico ou liste ?? meilleur pour un arbre ??
        self.__origin_state = state
        self._state = self.reset_state() # state qu'on peut modifier
        self._AIplayer = player
        self._player = self._AIplayer

    def reset_state(self):
        return copy.deepcopy(self.__origin_state)

    def search(self):
        '''
        Protocol of the AI

        :return: the move to the Client for _nextmove
        '''
        #print('Player', self._AIplayer)
        count = 1   # pour prévoir jusqu'à un certain niveau
        price = 1
        board_free = self.board_free()
        #print('board free', board_free)
        for place in board_free: # regarde tout les emplacements vides et valides (list)
            #print('place', place)
            move = {'move': 'place', 'to': list(place)}
            # self._moves[json.dumps(move)] = (place, price)
            #print('test2 state', self._state)
            self._state.update(json.loads(json.dumps(move)), self._player)  # on fait le mouvement pour regarder ce que ça fait
            #print('test3 state', self._state)
            # ERROR self._player doit correspondre à self.currentplayer ??
            # selon type d'emplacement, on lui attribue une valeur (price move)
            # on regarde quel type de mouvement c'est pour lui donner un prix
            self.is_place_upperlayer(place)  # cas particulier , prix est le meme, juste check si c'est un layer au dessus
            self.is_move_upperlayer(place)
            self.is_place_square_r1(place)
            self.is_place_square_r2(place)
            self.is_move_square_r1(place)
            self.is_move_square_r2(place)
            self.is_place(place)
            self._state = self.reset_state()  # reset du state pour essayer un autre mouvement
            # counter va être fixe pour chaque couche de profondeur ??
        #print('moves', self._moves)
        move = self.choose()
        #print('move choosen', move)
        return move


    def is_place_upperlayer(self, place):
        return

    def is_move_upperlayer(self, place):
        for balls in self.board_remove():
            if balls[0] == int((place[0])-1):
                price = 0
                move = {'move': 'move', 'from': list(balls), 'to': list(place)}
                self._moves[json.dumps(move)] = (place, price)
        return

    def is_place_square_r1(self, place):
        if self._state.CreateSquare(place):
            if len(self.board_remove()) == 1:
                price = 0
                move = {'move': 'place', 'to': list(place), 'remove': self.board_remove()[0]}
                self._moves[json.dumps(move)] = (place, price)
        return

    def is_place_square_r2(self, place):
        return

    def is_move_square_r1(self, place):
        return

    def is_move_square_r2(self, place):
        return

    def is_place(self, place):
        price = 1
        move = {'move': 'place', 'to': list(place)}
        self._moves[json.dumps(move)] = (place, price)
        return

    def board_free(self):
        '''
        travel the board and save all the free places in a list

        :return: the list of the free places
        '''
        board = list()
        for layer in range(4):
            for row in range(4-layer):
                for column in range(4-layer):
                    try:
                        self._state.validPosition(layer, row, column)
                        if self._state.get(layer, row, column) is None:
                            board.append((layer, row, column))
                    except:
                        pass
        return board

    def board_remove(self):
        '''
        travel the board and save all the pieces we can move

        :return: the list of the pieces we can move
        '''
        board = list()
        for layer in range(4):
            for row in range(4-layer):
                for column in range(4-layer):
                    try:
                        self._state.remove((layer, row, column), self._player)
                        # self._player or self._playernb
                        board.append((layer, row, column))
                    except:
                        pass
        return board

    def switch_player(self):
        '''
        Switch the player to see furthers moves

        :return: nothing
        '''
        self._player = (self._player + 1) % int(game.GameServer.nbplayers)
        return

    def price_tot(self, price2, price1=0):
        '''
        Sum the prices of the consecutives moves

        :param price2: price of the second move
        :param price1: price of the first move (0 if stage 1)
        :return: the total price
        '''
        if self._player == self._AIplayer:
            price1 += price2
        else:
            price1 -= price2
        return price1

    def choose(self):
        '''
        Choose the 'best' move of all the possible moves

        :return: the 'best' move
        '''
        move, price, place = '', 10, tuple()
        for moves in self._moves:
            if self._moves[moves][1] < price:
                move, price, place = moves, self._moves[moves][1], self._moves[moves][0]
            elif self._moves[moves][1] == price:
                if self._moves[moves][0][0] > place[0]:  # si upperlayer alors on le choisit
                    move, price, place = moves, self._moves[moves][1], self._moves[moves][0]
        return move