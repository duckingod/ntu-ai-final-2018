import math
import enum
from itertools import chain as original_chain
import random
from AIAlgo import SimpleAlgo, Beam, MCTS
random.seed(1)

chain = lambda l: list(original_chain.from_iterable(l))

def clone(o):
    if type(o) is dict:
        return {k: clone(v) for k, v in o.items()}
    elif type(o) is list:
        return [clone(v) for v in o]
    return o

def in_range(n, r):
    a, b = r if r[0] < r[1] else (r[1], r[0])
    return max(a, min(b, n))
class Nation(object):
    """
        >>> n = Nation(args={'p':123, 'a':0.5, 'r':[0, -1, 1, None, 1]})
        >>> new_n = Nation(n) # Copy nation
    """
    PROPERTYS = ['idx', 'die', 'in_war', 'e', 'e0', 'm', 't', 'i', 'a', 'p', 'r', 'd']
    PARAMS = {'a': 0.3, 'b': 0, 'c': 1}
    def __init__(self, n=None, args={}):
        if n is not None:
            for p in self.PROPERTYS:
                setattr(self, p, clone(getattr(n, p)))
        for p, v in args.items():
            setattr(self, p, clone(v))
        for p in self.PROPERTYS:
            if not hasattr(self, p):
                setattr(self, p, 0)
        for i, r in enumerate(self.r):
            self.r[i] = in_range(r, (-1, 1))
        self.r[self.idx] = 0
        self.a = in_range(self.a, (0, 1))
        for p in ['e', 'm', 'i', 'p']: # make these greater than zero
            setattr(self, p, max(0, getattr(self, p)))
    def __str__(self):
        return 'Nation: ' + {p:getattr(self, p) for p in self.PROPERTYS}.__str__()
    def __repr__(self):
        def r_str():
            return ' '.join([f'{r:5.2f}' for r in self.r])
        return f"{'X' if self.die else 'O'} e:{self.e:7.2f}  m:{self.m:7.2f}  a:{self.a:7.2f}  r: {r_str()}"
    def others(self, nations, targets):
        return [v for i, (n, v) in enumerate(zip(nations, targets)) if i != self.idx and not n.die]
    def updated(self, nations):
        ns = nations
        idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        ga, gb, gc = [self.PARAMS[k] for k in ['a', 'b', 'c']]
        nis, nms = ([n.i for n in nations], [n.m for n in nations])
        m1 = m + e * a
        return Nation(n=self, args={
            'in_war': False,
            'e': e * (1 - a) * (1 + i + t) if not in_war else e,
            'm': m + e * a,
            't': ga * sum([_r * _d * _i for _r, _d, _i in self.others(ns, zip(r, d, nis))]) + gb,
            'p': m1 + gc * sum([_r * _d * _m for _r, _d, _m in self.others(ns, zip(r, d, nms))])
        })

from action_effect import DefaultEffect

Action = enum.Enum('Action', 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT EXTORT POLICY')


class State:
    INVADE_B = -1

    invade = DefaultEffect.invade
    denounce = DefaultEffect.denounce
    make_friend = DefaultEffect.make_friend
    supply = DefaultEffect.supply
    construct = DefaultEffect.construct
    extort = DefaultEffect.extort
    policy = DefaultEffect.policy
    

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
            self.nations = clone(state.nations)
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
        for _action in Action:
            if action == _action:
                action_function = getattr(self, action.name.lower())
                action_function(nations, src, tar)
        if not action in Action:
            raise Exception('Not valid action: ' + str(action))
        nations[src] = nations[src].updated(nations)
        while True:
            new_state.now_player_i = (new_state.now_player_i + 1) % len(new_state.nations)
            # print(nations[new_state.now_player_i])
            if not nations[new_state.now_player_i].die: 
                break
        return new_state
    def actions(self):
        """
        Avaliable actions for player
        """
        idxs = [i for i, n in enumerate(self.nations) if i != self.now_player_i and not n.die]
        interact_actions = [Action.INVADE, Action.DENOUNCE, Action.MAKE_FRIEND, Action.SUPPLY, Action.EXTORT, ]
        interact_actions = [(a, i) for a in interact_actions for i in idxs]
        self_actions = [(Action.CONSTRUCT, None), (Action.POLICY, 1), (Action.POLICY, -1)]
        return interact_actions + self_actions
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
        for t in range(n_turns):
            p = self.state.now_player
            act = p.action(self.state)
            print(self.state.show())
            self.state = self.state.next_turn(act)
            print('After player_' + str(p.idx) + " " + p.name + ' did ' + str(act))
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

class HumanPlayer(Player):
    '''
    '''
    def __init__(self, ai_name, h):
        self.ai_name = ai_name
        self.algo = algo
        self._h = h
    def h(self, state, last_action):
        return self._h(self, state, last_action)
    @property
    def name(self):
        return 'CPU:'+self.ai_name
    def action(self, state):
        while True:
            dict_i_a = dict(list(enumerate(state.actions())))
            print("valid actions:")
            print(dict_i_a)
            action_input = input("plz input one action index or one action from 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT EXTORT POLICY':\n>>>")
            try:
                action_input = int(action_input)
                return dict_i_a[action_input]
            except:
                try:
                    if not Action[action_input] in state.actions():
                        print("please input valid action")
                        continue
                except:
                    print("please input valid action")
                    continue
            target = input("input target nation index: \n>>>")
            target = None if target == "" else int(target)
            return (Action[action_input], target)

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

def simple_h(player, state, action_taken):
    n = state.nations[player.idx]
    # return n.e + n.m
    return n.e 

if __name__=='__main__':
    # algo = Beam
    algo = MCTS
    players = [
        AIPlayer('Alice', algo(), simple_h),
        AIPlayer('Bob', algo(), simple_h),
        # AIPlayer('Carol', algo(), simple_h),
        HumanPlayer('xxxx', simple_h)
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
            {'e': 20, 'e0': 20, 'm': 6,  'i': 0.3, 'a': 0.0},
            {'e': 3,  'e0': 3,  'm': 6,  'i': 0.4, 'a': 0.25}
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    game = Game(players, initial_state)
    game.run()

