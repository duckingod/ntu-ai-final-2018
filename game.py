import math

from action_effect import export_effect
from utils import Action, INTERACT_ACTIONS, SELF_ACTIONS
import utils

import random
from AIAlgo import SimpleAlgo, Beam, MCTS
random.seed(1)


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
    PARAMS = {'a': 0.5, 'b': 0, 'c': 0.3, 'd':0.1, 'e':0.4}
    def __init__(self, n=None, args={}):
        if n is not None:
            for p in self.PROPERTYS:
                setattr(self, p, getattr(n, p))
        for p, v in args.items():
            setattr(self, p, clone(v))
        for p in self.PROPERTYS:
            if not hasattr(self, p):
                setattr(self, p, 0)
        self.parameter_check()
    def change(self, args):
        return Nation(self, args)
    def parameter_check(self):
        for i, r in enumerate(self.r):
            self.r[i] = in_range(r, (-1, 1))
        self.r[self.idx] = 0
        self.d[self.idx] = 0
        self.a = in_range(self.a, (0, 0.4))
        for p in ['e', 'm', 'i', 'p']: # make these greater than zero
            setattr(self, p, max(0, getattr(self, p)))
    def __str__(self):
        return 'Nation: ' + {p:getattr(self, p) for p in self.PROPERTYS}.__str__()
    def __repr__(self):
        def r_str():
            return ' '.join([f'{r:5.2f}' for r in self.r])
        idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        return f"{'X' if die else 'O'}{'-' if in_war else ' '} e:{e:7.2f}  e0:{e0:5.1f}  m:{m:7.2f}  p:{p:7.2f}  a:{a:4.2f}  i:{i:4.2f}  t:{t:5.2f}  r: {r_str()}"
    def others(self, nations, targets):
        return [v for i, (n, v) in enumerate(zip(nations, targets)) if i != self.idx and not n.die]
    def growth(self, _a=None):
        idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        if _a is None: _a = a
        return max(1, (1 - a) * (1 + i + t) / math.exp(0.1 * (e/e0-1)))
    def updated(self, nations):
        ns = nations
        idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        ga, gb, gc, gd, ge = [self.PARAMS[k] for k in ['a', 'b', 'c', 'd', 'e']]
        nis, nms = ([n.i for n in nations], [n.m for n in nations])
        e1 = e * self.growth() if not in_war else e
        e1 = e1 - m * gd
        m1 = m + ge * e * a if not in_war else m
        m1 = min(e1, m1)
        return self.change({
            'in_war': False,
            'e': e1,
            'm': m1,
        }).refresh(nations)
    def refresh(self, nations):
        ns = nations
        idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(self, p) for p in self.PROPERTYS]
        ga, gb, gc, gd, ge = [self.PARAMS[k] for k in ['a', 'b', 'c', 'd', 'e']]
        nis, nms = ([n.i for n in nations], [n.m for n in nations])
        return self.change({
            't': ga * sum([_r * _d * _i for _r, _d, _i in self.others(ns, zip(r, d, nis))]) + gb,
            'p': m + gc * sum([max(0, _r) * _d * _m for _r, _d, _m in self.others(ns, zip(r, d, nms))])
        })


class State:
    INVADE_B = -1

    action_function = {k: export_effect[k.name.lower()] for k in Action }

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
        self.performed_action = (None, None)
        for k, v in args.items():
            setattr(self, k, v)
    @property
    def now_player(self):
        return self.players[self.now_player_i]
    def __repr__(self):
        return self.show(show=lambda n: str(n))
    def show(self, show=lambda n: repr(n)):
        def ptr(i, n): return ('> ' if i==self.now_player_i else '  ')
        def h(i): return f'  {self.players[i].h(self):.4f}'
        return '\n'.join([ptr(i, n) + repr(n) + h(i) for i, n in enumerate(self.nations)])
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
        action, arg = action
        src = self.now_player_i
        self.action_function[action](nations, src, arg)
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
        interact_actions = [(a, i) for a in INTERACT_ACTIONS for i in idxs]
        self_actions = [(Action.CONSTRUCT, None), (Action.POLICY, 1), (Action.POLICY, -1), (Action.PRODUCE, None)]
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
            n = self.state.nations[self.state.now_player_i]
            idx, die, in_war, e, e0, m, t, i, a, p, r, d = [getattr(n, p) for p in n.PROPERTYS]
            print((1 - a) * (1 + i + t) / math.exp(0.1 * (e/e0-1)), (1 - a) * (1 + i + t), math.exp(0.1 * (e/e0-1)))
            p = self.state.now_player
            act = p.action(self.state)
            print(self.state.show())
            self.state = self.state.next_turn(act)
            print('After ' + p.name + ' did ' + utils.action_string(act, self.players))
            print(self.state.show())
            print()

class Player:
    '''
    Member:
     - name
     - idx
     - h(state)
     - action(state)
    '''
    def h(self, state):
        """ hueristic??  """
        raise NotImplementedError("To be implemented duckingod")
    def action(self, state):
        raise NotImplementedError("To be implemented QAQ")

class HumanPlayer(Player):
    '''
    '''
    def __init__(self, ai_name, h):
        self.ai_name = ai_name
        self._h = h
        self.is_human = True
    def h(self, state):
        return self._h(self, state)
    @property
    def name(self):
        return self.ai_name
    def action(self, state):
        i2action = list(state.actions())
        print("Valid actions:")
        for i, a in enumerate(i2action):
            print(f"{i:3d} -> {utils.action_string(a, state.players)}")
        while True:
            action_input = input("plz input one action index or one action from 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT EXTORT POLICY':\n>>>")
            if action_input.isdigit() and 0 <= int(action_input) < len(i2action):
                return i2action[int(action_input)]
            try:
                act = Action[action_input.upper()]
                target = input("input target nation index: \n>>>")
                target = None if target == "" else int(target)
                if (act, target) in state.actions():
                    return (act, target)
            except:
                pass
            print("please input valid action")

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
    def h(self, state):
        return self._h(self, state)
    @property
    def name(self):
        return 'CPU:'+self.ai_name
    def action(self, state):
        return self.algo.get_action(state)

def simple_h(player, state):
    # print(player)
    # print(player.idx)
    n = state.nations[player.idx]
    # return n.e + n.m
    # neg = 0
    # for n_tmp in state.nations:
    #     if n_tmp != n:
    #         neg += n_tmp.e + n_tmp.m
    # print(n.e + n.m)
    # print(n.m)
    return n.e + n.m

def simple_h_em(player, state):
    n = state.nations[player.idx]
    return n.e + n.m / 3


if __name__=='__main__':
    import init_config
    # algo = lambda: Beam(2000, 20)
    algo = lambda: MCTS(turns=12, iter_n=999)
    players, initial_state = init_config.spring(algo)
    game = Game(players, initial_state)
    game.run()

