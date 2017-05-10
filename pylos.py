#!/usr/bin/env python3
# pylos.py
# Author: Quentin Lurkin
# Version: April 28, 2017
# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import json

from lib import game

class PylosState(game.GameState):
    '''Class representing a state for the Pylos game.'''
    def __init__(self, initialstate=None):
        
        if initialstate == None:
            # define a layer of the board
            def squareMatrix(size):
                matrix = []
                for i in range(size):
                    matrix.append([None]*size)
                return matrix

            board = []
            for i in range(4):
                board.append(squareMatrix(4-i))

            initialstate = {
                'board': board,
                'reserve': [15, 15],
                'turn': 0
            }

        super().__init__(initialstate)

    def get(self, layer, row, column):
        if layer < 0 or row < 0 or column < 0:
            raise game.InvalidMoveException('The position ({}) is outside of the board'.format([layer, row, column]))         
        try:
            return self._state['visible']['board'][layer][row][column]
        except:
            raise game.InvalidMoveException('The position ({}) is outside of the board'.format([layer, row, column]))

    def safeGet(self, layer, row, column):
        try:
            return self.get(layer, row, column)
        except game.InvalidMoveException:
            return None

    def validPosition(self, layer, row, column):
        if self.get(layer, row, column) != None:
            raise game.InvalidMoveException('The position ({}) is not free'.format([layer, row, column]))

        if layer > 0:
            if (
                self.get(layer-1, row, column) == None or
                self.get(layer-1, row+1, column) == None or
                self.get(layer-1, row+1, column+1) == None or
                self.get(layer-1, row, column+1) == None
            ):
                raise game.InvalidMoveException('The position ({}) is not stable'.format([layer, row, column]))

    def canMove(self, layer, row, column):
        if self.get(layer, row, column) == None:
            raise game.InvalidMoveException('The position ({}) is empty'.format([layer, row, column]))

        if layer < 3:
            if (
                self.safeGet(layer+1, row, column) != None or
                self.safeGet(layer+1, row-1, column) != None or
                self.safeGet(layer+1, row-1, column-1) != None or
                self.safeGet(layer+1, row, column-1) != None
            ):
                raise game.InvalidMoveException('The position ({}) is not movable'.format([layer, row, column]))

    def createSquare(self, coord):
        layer, row, column = tuple(coord)

        def isSquare(layer, row, column):
            if (
                self.safeGet(layer, row, column) != None and
                self.safeGet(layer, row+1, column) == self.safeGet(layer, row, column) and
                self.safeGet(layer, row+1, column+1) == self.safeGet(layer, row, column) and
                self.safeGet(layer, row, column+1) == self.safeGet(layer, row, column)
            ):
                return True
            return False

        if (
            isSquare(layer, row, column) or
            isSquare(layer, row-1, column) or
            isSquare(layer, row-1, column-1) or
            isSquare(layer, row, column-1)
        ):
            return True
        return False

    def set(self, coord, value):
        layer, row, column = tuple(coord)
        self.validPosition(layer, row, column)
        self._state['visible']['board'][layer][row][column] = value

    def remove(self, coord, player):
        layer, row, column = tuple(coord)
        self.canMove(layer, row, column)
        sphere = self.get(layer, row, column)
        if sphere != player:
            raise game.InvalidMoveException('not your sphere')
        self._state['visible']['board'][layer][row][column] = None
        
    # update the state with the move
    # raise game.InvalidMoveException
    def update(self, move, player):
        state = self._state['visible']
        if move['move'] == 'place':
            if state['reserve'][player] < 1:
                raise game.InvalidMoveException('no more sphere')
            self.set(move['to'], player)
            state['reserve'][player] -= 1
        elif move['move'] == 'move':
            if move['to'][0] <= move['from'][0]:
                raise game.InvalidMoveException('you can only move to upper layer')
            sphere = self.remove(move['from'], player)
            try:
                self.set(move['to'], player)
            except game.InvalidMoveException as e:
                self.set(move['from'], player) 
                raise e
        else:
            raise game.InvalidMoveException('Invalid Move:\n{}'.format(move))

        if 'remove' in move:
            if not self.createSquare(move['to']):
                raise game.InvalidMoveException('You cannot remove spheres')
            if len(move['remove']) > 2:
                raise game.InvalidMoveException('Can\'t remove more than 2 spheres')
            for coord in move['remove']:
                sphere = self.remove(coord, player)
                state['reserve'][player] += 1

        state['turn'] = (state['turn'] + 1) % 2


    # return 0 or 1 if a winner, return None if draw, return -1 if game continue
    def winner(self):
        state = self._state['visible']
        if state['reserve'][0] < 1:
            return 1
        elif state['reserve'][1] < 1:
            return 0
        return -1

    def val2str(self, val):
        return '_' if val == None else '@' if val == 0 else 'O'

    def player2str(self, val):
        return 'Light' if val == 0 else 'Dark'

    def printSquare(self, matrix):
        print(' ' + '_'*(len(matrix)*2-1))
        print('\n'.join(map(lambda row : '|' + '|'.join(map(self.val2str, row)) + '|', matrix)))

    # print the state
    def prettyprint(self):
        state = self._state['visible']
        for layer in range(4):
            self.printSquare(state['board'][layer])
            print()
        
        for player, reserve in enumerate(state['reserve']):
            print('Reserve of {}:'.format(self.player2str(player)))
            print((self.val2str(player)+' ')*reserve)
            print()
        
        print('{} to play !'.format(self.player2str(state['turn'])))
        #print(json.dumps(self._state['visible'], indent=4))       

class PylosServer(game.GameServer):
    '''Class representing a server for the Pylos game.'''
    def __init__(self, verbose=False):
        super().__init__('Pylos', 2, PylosState(), verbose=verbose)
    
    def applymove(self, move):
        try:
            self._state.update(json.loads(move), self.currentplayer)
        except json.JSONDecodeError:
            raise game.InvalidMoveException('move must be valid JSON string: {}'.format(move))


class PylosClient(game.GameClient):
    '''Class representing a client for the Pylos game.'''
    def __init__(self, name, server, verbose=False):
        super().__init__(server, PylosState, verbose=verbose)
        self.__name = name
        self._moves = {}
    
    def _handle(self, message):
        pass

    #return move as string
    def _nextmove(self, state):
        '''
        example of moves
        coordinates are like [layer, row, colums]
        move = {
            'move': 'place',
            'to': [0,1,1]
        }

        move = {
            'move': 'move',
            'from': [0,1,1],
            'to': [1,1,1]
        }

        move = {
            'move': 'move',
            'from': [0,1,1],
            'to': [1,1,1]
            'remove': [
                [1,1,1],
                [1,1,2]
            ]
        }
        
        return it in JSON
        '''
        self._state = state
        self._moves = {}
        # dictionnary of move made by turn
        # dictionnary moves instance of the class reset at each turn ??
        try:
            # test different specific moves
            test = self.upperlayer()
            #print('TEST upperlayer', test)
            if test == True:
                return self.choose()
            else:
                return self.noStrat()

        except:
            return self.noStrat()

    def upperlayer(self):
        '''
        Look if he can put a sphere on a upper layer

        return True if he finds a move (saved in the dictionnary moves)
        '''
        #print('TEST upperlay')
        price = 1
        out = False
        for layer in range(4):
            for row in range(4 - layer):
                for column in range(4 - layer):
                    try:
                        self._state.validPosition(layer+1, row, column)
                        if self._state.get(layer+1, row, column) == None:
                            #   if square alors go et prendre sur layer plus basse possible
                            self._moves[json.dumps({'move': 'place', 'to': [layer+1, row, column]})] = price
                            out = True
                            cible = [(layer+1, row, column),
                                     (layer, row, column),
                                     (layer, row+1, column),
                                     (layer, row+1, column+1),
                                     (layer, row, column+1)]
                            self.deplace(price, cible)
                    except:
                        pass
        return out

    def deplace(self, price, cible):
        '''
        Look if he can deplace a sphere

        return nothing
        '''
        # Est-elle vraiment utile ??
        #print('TEST deplace, upperlay')
        price -= 1
        for layer in range(4):
            for row in range(4 - layer):
                for column in range(4-layer):
                    if layer < cible[0][0]:
                        if (layer, row, column) not in cible:
                            try:
                                self._state.remove((layer, row, column), self._playernb)
                                self._moves[json.dumps({'move': 'move', 'from': [layer, row, column], 'to': list(cible[0])})] = price
                            except Exception as e:
                                #print(e)
                                pass
        return


    def choose(self):
        '''
        look the cheapest move of all the strategic moves

        return the next move
        '''
        #print('DICO moves', moves)
        price = 10
        choice = False
        for elem in self._moves:
            if self._moves[elem] <= price:
                choice = elem
                price = self._moves[elem]
            elif self._moves[elem] == price:
                pass
                # voir si on choisi selon le type de mouvement qu'on fait
            else:
                pass
        if choice:
            return choice
        else:
            return self.noStrat()
            # définir une nouveau type erreur pour gérer les erreurs de L'IA ??

    def noStrat(self):
        '''
        next move by default
        '''
        #print('FAILED NO STRATEGY')
        for layer in range(4):
            for row in range(4 - layer):
                for column in range(4 - layer):
                    if self._state.get(layer, row, column) == None:
                        return json.dumps({
                            'move': 'place',
                            'to': [layer, row, column]
                        })


if __name__ == '__main__':
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Pylos game')
    subparsers = parser.add_subparsers(description='server client', help='Pylos game components', dest='component')
    # Create the parser for the 'server' subcommand
    server_parser = subparsers.add_parser('server', help='launch a server')
    server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
    server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
    server_parser.add_argument('--verbose', action='store_true')
    # Create the parser for the 'client' subcommand
    client_parser = subparsers.add_parser('client', help='launch a client')
    client_parser.add_argument('name', help='name of the player')
    client_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client_parser.add_argument('--verbose', action='store_true')
    # Parse the arguments of sys.args
    args = parser.parse_args()
    if args.component == 'server':
        PylosServer(verbose=args.verbose).run()
    else:
        PylosClient(args.name, (args.host, args.port), verbose=args.verbose)