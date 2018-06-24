from game import *
from player import get_h

def xogo(algo):
    players = [
        AIPlayer('Alice', algo(), get_h()),
        AIPlayer('Bob', algo(), get_h()),
        # AIPlayer('Carol', algo(), get_h()),
        HumanPlayer('xxxx', get_h())
        ]
    dist = [
            [0, 0.7, 0.5],
            [0.7, 0, 0.7],
            [0.5, 0.7, 0]
            ]
    relations = [
            [0, 1, -1],
            [1, 0, 0],
            [-1, 0, 0]
            ]
    relations = [[0,0,0], [0,0,0], [0,0,0]]
    nation_props = [
            {'e': 10, 'e0': 10, 'm': 10, 'i': 0.2, 'a': 0.25},
            {'e': 10, 'e0': 10, 'm': 10, 'i': 0.2, 'a': 0.25},
            {'e': 10, 'e0': 10, 'm': 10, 'i': 0.2, 'a': 0.25},
        #     {'e': 20, 'e0': 20, 'm': 6,  'i': 0.3, 'a': 0.0},
        #     {'e': 3,  'e0': 3,  'm': 6,  'i': 0.4, 'a': 0.25}
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    return players, initial_state

def duck(algo):
    players = [
		AIPlayer('QIN', algo(), get_h()),
		AIPlayer('HAN', algo(), get_h()),
		AIPlayer('ZHAO', algo(), get_h()),
		AIPlayer('WEI', algo(), get_h()),
		# HumanPlayer('xxxx', simple_h)
        ]
    dist = [
			[0, 0.9, 0.8, 0.7],
			[0.9, 0, 0.8, 0.9],
			[0.8, 0.8, 0, 0.8],
			[0.7, 0.9, 0.8, 0],
			]
    relations = [
			[0, -0.4, -0.4, 0],
			[-0.4, 0, 0.4, 0.3],
			[-0.4, 0.4, 0, 0.3],
			[0, 0.3, 0.3, 0],
            ]
    # relations = [[0,0,0], [0,0,0], [0,0,0]]
    nation_props = [
			{'e': 45, 'e0': 15, 'm': 14, 'i':  1.5, 'a': 0.2},
			{'e': 9, 'e0': 3, 'm': 5,  'i': 1.4, 'a': 0},
			{'e': 27,  'e0': 8,  'm': 10,  'i': 1.4, 'a': 0.2},
			{'e': 21, 'e0': 6, 'm': 8, 'i':  1.6, 'a': 0.2},
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    print(initial_state)
    return players, initial_state
    