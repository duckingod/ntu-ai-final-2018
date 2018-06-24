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
            {'e': 80, 'e0': 10, 'm': 8, 'i':  1.0, 'a': 0.2},
            {'e': 160, 'e0': 20, 'm': 4,  'i': 1.2, 'a': 0.2},
            {'e': 30,  'e0': 3,  'm': 3,  'i': 1.7, 'a': 0.2}
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    return players, initial_state

def spring(algo):
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
    return players, initial_state

def duck_spring(algo):
    """
        2
        3
    0   1
    def get_h(personality=['f', '', 'tao', 'love', ''], params=[None, 0.5, 1, 10, 1]):
        fs = [common, invade, diplomatic, love_union, potential]
    """
    
    # per = ['f', '', 'tao', 'love', '']
    # per_p = [0, 0.5, 1, 4, 0.5]
    # fs = [common, invade, diplomatic, love_union, potential_t, potential_e0, security]
    per=['f', '', 'tao', 'love', '', '', '', 'war']
    per_p=[None, 0.5, 1, 10, 3, 0.5, 2]
    p = (per, per_p)
    players = [
            AIPlayer('Qin', algo(), get_h(*p)),
            AIPlayer('Han', algo(), get_h(*p)),
            AIPlayer('Zhao', algo(), get_h(*p)),
            AIPlayer('Qi', algo(), get_h(*p)),
            # HumanPlayer('xxxx', simple_h)
            ]
    dist = [
            [0, 0.8, 0.6, 0.4],
            [0.8, 0, 0.8, 0.8],
            [0.6, 0.8, 0, 0.6],
            [0.4, 0.8, 0.6, 0],
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
    return players, initial_state
