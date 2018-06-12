# try
# try try
import math
from itertools import chain as original_chain
chain = lambda l: list(original_chain.from_iterable(l))

def clone(o):
    if type(o) is dict:
        return {k: clone(v) for k, v in o.items()}
    elif type(o) is list:
        return [clone(v) for v in o]
    elif type(o) is Nation:
        # return Nation(o)
        return o
    return o

class Nation(object):
    """
        >>> n = Nation(args={'p':123, 'a':0.5, 'r':[0, -1, 1, None, 1]})
        >>> new_n = Nation(n) # Copy nation
    """
    PROPERTYS = ['idx', 'die', 'e', 'm', 't', 'i', 'a', 'p', 'r', 'd']
    PARAMS = {'a': 1, 'b': 1, 'c': 1}
    def __init__(self, n=None, args={}):
        if n is not None:
            for p in self.PROPERTYS:
                setattr(self, p, clone(getattr(n, p)))
        for p, v in args.items():
            setattr(self, p, clone(v))
        for p in self.PROPERTYS:
            if not hasattr(self, p):
                setattr(self, p, 0)
    def __str__(self):
        return 'Nation: ' + {p:getattr(self, p) for p in self.PROPERTYS}.__str__()
    def __repr__(self):
        return f"{'X' if self.die else 'O'} e:{self.e:7.2f}  m:{self.m:7.2f}  a:{self.a:7.2f}  r: {self.r}"
    def others(self, nations, targets):
        return [v for i, (n, v) in enumerate(zip(nations, targets)) if i != self.idx and not n.die]
    def updated(self, nations):
        ns = nations
        idx, die, e, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        ga, gb, gc = [self.PARAMS[k] for k in ['a', 'b', 'c']]
        nis, nms = ([n.i for n in nations], [n.m for n in nations])
        m1 = m + e * a
        return Nation(n=self, args={
            'e': e * (1 - a) * (1 + i + t),
            'm': m + e * a,
            't': ga * sum([_r * _d * _i for _r, _d, _i in self.others(ns, zip(r, d, nis))]) + gb,
            'p': m1 + gc * sum([_r * _d * _m for _r, _d, _m in self.others(ns, zip(r, d, nms))])
        })


"""
| Nation | $n_i$ |
|--------|-------|
| Nation power: | $p_i=a_i\lambda_{power} \sum r_{ij}d_{ij}p_j + p_i + rand$ (next turn) |
| Military power: | $m_i = (1-a_i)p_i$ |
| Nation relation (not sym) | $r_{ij}$ |
| Nation Status of $n_i$ | $s_i = \{c_j\}$|
| Distance | $d_{ij}$ |
| Affair Ratio | $a_i$ |
"""

class State:
    INVADE_B = -1
    def __init__(self, state=None, args={}):
        """
        小魯來惹(｡◕∀◕｡)
        args
            now_player(int): index of player who can take action
            nations(dict): key: player_i, value: Nation object
        """
        if state is not None:
            self.now_player_i = state.now_player_i
            self.players = state.players
            self.last_state = state
            self.nations = clone(nations)
        else:
            self.last_state = None
        self.performed_action = None
        for k, v in args.items():
            setattr(self, k, v)
    @property
    def now_player(self):
        return self.players[self.now_player_i]
    def __repr__(self):
        return self.show(show=lambda n: str(n))
    def show(self, show=lambda n: repr(n)):
        def ptr(i, n): return ('> ' if i==self.now_player_i else '  ')
        return '\n'.join([ptr(i, n) + repr(n) for i, n in enumerate(self.nations)])
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
    def next_turn(self, action):
        """
        compute new state object by now_player and given action.
        should not change state of self.
        args
            action(tuple): (action_name, action_param) the action that player takes.
        returns
            new_state
        """
        from random import random
        new_state = State(self)
        nations = new_state.nations
        """doing action to update nations"""
        self.performed_action = action
        action, tar = action
        src = self.now_player_i
        src_n, tar_n = nations[src], nations[tar]
        if action == "invade":
            success_prob = self.sigmoid(self.INVADE_B + (src_n.m * src_n.d[tar] - tar_n.m) / tar_n.m)
            rnd = random()
            if rnd > success_prob:
                nations[tar] = Nation(tar_n, {'die': True, 'd': [0] * len(nations)})
            else:
                src_r, tar_r = (1+rnd)/2 * success_prob, (2-rnd)/2 * (1 - success_prob)
                nations[src] = Nation(src_n, {'e': src_n.e * src_r, 'm': src_n.m * src_r})
                nations[tar] = Nation(tar_n, {'e': tar_n.e * tar_r, 'm': tar_n.m * tar_r})
        elif action == "denounce":
            nations[src] = Nation(src_n, {'r': [             r if i!=tar else max(r-0.5, -1) for i, r in enumerate(src_n.r)]})
            nations[src] = Nation(tar_n, {'r': [max(r-0.1, -1) if i!=src else max(r-0.5, -1) for i, r in enumerate(tar_n.r)]})
        elif action == "make_friend":
            nations[src] = Nation(src_n, {'r': [r if i!=tar else min(r+0.5, 1) for i, r in enumerate(src_n.r)]})
            nations[tar] = Nation(tar_n, {'r': [r if i!=src else min(r+0.5, 1) for i, r in enumerate(tar_n.r)]})
        elif action == "supply":
            nations[tar] = Nation(tar_n, {'e': 1.3 * src_n.e})
        elif action == "construct":
            if tar > 0:
                nations[src] = Nation(src_n, {'a': min(1, src_n.a + 0.25)})
            else:
                nations[src] = Nation(src_n, {'a': max(0, src_n.a - 0.25)})
        else:
            raise Exception('Not valid action: ' + action)
        new_state.nations[src] = nations[src].updated(nations)
        while True:
            new_state.now_player_i = (new_state.now_player_i + 1) % len(new_state.nations)
            if not nations[self.now_player_i].die: break
        return new_state
    def actions(self):
        """
        Avaliable actions for player
        """
        idxs = [i for i, n in enumerate(self.nations) if i != self.now_player_i and not n.die]
        interact_actions = [(a, i) for a in ['invade', 'denounce', 'make_friend', 'supply'] for i in idxs]
        return interact_actions + [('construct', 1), ('construct', -1)]
    def trace(self, l=None):
        if l==None: l = []
        if self.last_state==None:
            l.append(self)
        else:
            self.last_state.trace(l)
            l.append(self)
        return l

class Game:
    '''
    (／‵Д′)／~ ╧╧
    '''
    def __init__(self, players, initial_state):
        self.state = initial_state
        self.players = players
        for i, p in enumerate(self.players):
            p.idx = i
    def run(self, n_turns=200):
        print('Game setting')
        print(self.state)
        for t in range(n_turns):
            p = self.state.now_player
            act = p.action(self.state)
            self.state = self.state.next_turn(act)
            print(self.state.show())
            print('After player ' + p.name + ' did ' + str(act))
            print(self.state.show())
            print()
            input()

class Player:
    '''
    Member:
     - name
     - idx
     - h(state, last_action)
     - action(state)
    '''
    def h(self, state, action_taken=None):
        """ hueristic??  """
        raise NotImplementedError("To be implemented duckingod")
    def action(self, state):
        raise NotImplementedError("To be implemented QAQ")


class AIPlayer(Player):
    '''
    ( ･ิω･ิ)
    (́◉◞౪◟◉‵)
    ヽ(✿ﾟ▽ﾟ)ノ
    ヽ(∀ﾟ )人(ﾟ∀ﾟ)人( ﾟ∀)人(∀ﾟ )人(ﾟ∀ﾟ)人( ﾟ∀)ﾉ
    (*‘ v`*)
    ｡:.ﾟヽ(*´∀`)ﾉﾟ.:｡
    ʕ•̫͡ʕ•̫͡ʕ•̫͡ʕ•̫͡•ʔ•̫͡•ʔ•̫͡•ʔ

      ̫̫̫̫
    ʕ•͡ ̫ •͡ ʔ
    
    '''
    def __init__(self, ai_name, algo, h):
        self.ai_name = ai_name
        self.algo = algo
        self._h = h
    def h(self, state, last_action):
        return self._h(self, state, last_action)
    @property
    def name(self):
        return 'CPU:'+self.ai_name
    def action(self, state):
        return self.algo.get_action(state)

class AIAlgo:
    def get_action(self, state):
        raise NotImplementedError("To be implemented (´・ω・`)")

class SimpleAlgo(AIAlgo):
    def get_action(self, state):
        return state.actions()[0]
class Beam(AIAlgo):
    '''
    (*ﾟ∀ﾟ*)
    duckingod
    RRRRRRRRR
    da'shen'hao'shen
    '''
    def __init__(self, topk=20, turns=30):
        self.topk = topk
        self.turns = turns
    def get_action(self, state):
        player = state.now_player
        states = [(state.next_turn(a), None, a) for a in state.actions() ]
        for i in range(self.turns):
            p = states[0][0].now_player
            states = chain([[(s.next_turn(a), a, original_a) for a in s.actions()] for s, _, original_a in states])
            states.sort(key=lambda s: -p.h(s[0], s[1]))
            states = states[:self.topk]
        return max(states, key=lambda s: player.h(s[0], s[2]))[2] # Bug! s[2] is not correct QQ

def simple_h(player, state, action_taken):
    n = state.nations[player.idx]
    return n.e + n.m

if __name__=='__main__':
    players = [
        AIPlayer('Alice', Beam(), simple_h),
        AIPlayer('Bob', Beam(), simple_h),
        AIPlayer('Carol', Beam(), simple_h)
        ]
    dist = [
            [0, 0.5, 0.3],
            [0.5, 0, 0.5],
            [0.3, 0.5, 0]
            ]
    relations = [
            [0, 1, -1],
            [1, 0, 0],
            [-1, 0, 0]
            ]
    nation_props = [
            {'e': 10, 'm': 10, 'i': 5, 'a': 0.25},
            {'e': 20, 'm': 5,  'i':15, 'a': 0.0},
            {'e': 3, 'm': 3, 'i': 25, 'a': 0.25}
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    game = Game(players, initial_state)
    game.run()

