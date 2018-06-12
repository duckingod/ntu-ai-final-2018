import math
import enum
from itertools import chain as original_chain
import random
random.seed(0)

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

"""
class Action(enum.Enum):
    INVADE = 'invade'
    DENOUNCE = 'denounce'
    MAKE_FRIEND = 'make_friend'
    SUPPLY = 'supply'
    CONSTRUCT = 'construct'
    EXTORT = 'extort'
    POLICY = 'policy'
"""
Action = enum.Enum('Action', 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT EXTORT POLICY')

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
        src_n, tar_n = nations[src], (nations[tar] if action != Action.CONSTRUCT else None)
        if action == Action.INVADE:
            win, lose = (src, tar) if src_n.m > tar_n.m else (tar, src)
            wn, ln = nations[win], nations[lose]
            pw, pl = wn.m, ln.m
            el = ln.e
            wr, lr = pw / (pw + pl + 1), pl / (pw + pl + 1)
            nations[win] = Nation(wn, {'in_war': True, 'e': wn.e + el * wr / 2, 'm': wn.m - lr * pl})
            if ln.e - el * wr / 2 < ln.e0:
                nations[lose] = Nation(ln, {'die': True, 'd': [0] * len(nations)})
            else:
                nations[lose] = Nation(wn, {'in_war': True, 'e': ln.e - el * wr / 2, 'm': ln.m - wr * pl})
        elif action == Action.DENOUNCE:
            nations[src] = Nation(src_n, {'r': [r if i!=tar else r - (2-r) * 0.1 for i, r in enumerate(src_n.r)]})
            nations[tar] = Nation(tar_n, {'r': [r - (2 - r) * (0.05 if i!=src else 0.1) for i, r in enumerate(tar_n.r)]})
        elif action == Action.MAKE_FRIEND:
            nations[src] = Nation(src_n, {'r': [r if i!=tar else r + (2+r) * 0.1 for i, r in enumerate(src_n.r)]})
            nations[src] = Nation(src_n, {'r': [r if i!=src else r + (2+r) * 0.1 for i, r in enumerate(src_n.r)]})
        elif action == Action.SUPPLY:
            nations[src] = Nation(src_n, {
                'e': src_n.e - (1 - src_n.a) * src_n.i,
                'r': [r if i!=tar else r + (2+r) * 0.2 for i, r in enumerate(src_n.r)]
                })
            nations[tar] = Nation(tar_n, {
                'e': tar_n.e + (1 - src_n.a) * src_n.i,
                'r': [r if i!=src else r + (2+r) * 0.2 for i, r in enumerate(tar_n.r)]
                })
        elif action == Action.EXTORT:
            nations[src] = Nation(src_n, {
                'e': src_n.e + (1 - src_n.a) * src_n.i,
                'r': [r if i!=tar else r - (2-r) * 0.2 for i, r in enumerate(src_n.r)]
                })
            nations[tar] = Nation(tar_n, {
                'e': tar_n.e - (1 - src_n.a) * src_n.i,
                'r': [r if i!=src else r - (2-r) * 0.2 for i, r in enumerate(tar_n.r)]
                })
        elif action == Action.CONSTRUCT:
            i = src_n.i
            nations[src] = Nation(src_n, {'i': i + 0.1 * ((0.2-i) if i < 1 else 1)})
        elif action == Action.POLICY:
            nations[src] = Nation(src_n, {'a': src_n.a + 0.1 * tar})
        else:
            raise Exception('Not valid action: ' + str(action))
        nations[src] = nations[src].updated(nations)
        while True:
            new_state.now_player_i = (new_state.now_player_i + 1) % len(new_state.nations)
            if not nations[new_state.now_player_i].die: break
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
        from random import sample
        return sample(state.actions(), 1)[0]
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
class MCTS(AIAlgo):
    class mcts_node(object):
        def __init__(self, total_score=0.5, visit_n=1, state=None, parent=None, player=None, parent_action=None):
            """ set init visit_n=1 to avoid division by zero 
            set init total_score=0.5 to encourage discover new node
            """
            self.total_score = total_score
            self.visit_n = visit_n
            self.state = state
            self.parent = parent
            self.player = player
            self.parent_action = parent_action
            self.child_nodes = []
    def __init__(self, turns=50, iter_n=9999):
        """ 
        turns: depth of Tree
        iter_n: random simulation times
        """
        self.turns = turns
        self.iter_n = iter_n
    def selection(self, node):
        while node.child_nodes:
            """ maybe need to deal with dead nation situation later
            """
            node = max(node.child_nodes, key=lambda child_node: child_node.total_score / child_node.visit_n)
        return node
    def expansion(self, node):
        node.child_nodes = [ self.mcts_node(state=node.state.next_turn(a), parent=node, player=node.state.next_turn(a).now_player, parent_action=a) for a in node.state.actions() ]    
        return node.child_nodes[0]
    def simulation(self, node):
        state = node.state
        for i in range(self.turns):
            state = state.next_turn(random.choice(node.state.actions()))
            # print(state.nations[state.now_player_i])
        return state
    def backpropagation(self, state, node):
        while node.parent:
            """FIXME"""
            node.total_score += node.player.h(node.player,state) #""" what is h look like???"""
            node.visit_n += 1
            node = node.parent
        return None
    def get_action(self, state):
        self.root = self.mcts_node(state=state)
        for i in range(self.iter_n):
            node_select= self.selection(self.root)
            node_new = self.expansion(node_select)
            state_final = self.simulation(node_new)
            self.backpropagation(state_final, node_new)
        node_best = max(self.root.child_nodes, key=lambda child_node: child_node.total_score / child_node.visit_n)
        return node_best.parent_action

def simple_h(player, state, action_taken):
    n = state.nations[player.idx]
    return n.e + n.m

if __name__=='__main__':
    # players = [
    #     AIPlayer('Alice', Beam(), simple_h),
    #     AIPlayer('Bob', Beam(), simple_h),
    #     AIPlayer('Carol', Beam(), simple_h)
    #     ]
    players = [
        AIPlayer('Alice', MCTS(), simple_h),
        AIPlayer('Bob', MCTS(), simple_h),
        AIPlayer('Carol', MCTS(), simple_h)
    algo = Beam
    players = [
        AIPlayer('Alice', algo(), simple_h),
        AIPlayer('Bob', algo(), simple_h),
        AIPlayer('Carol', algo(), simple_h)
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
            {'e': 10, 'e0': 10, 'm': 10, 'i': 0.2, 'a': 0.25},
            {'e': 20, 'e0': 20, 'm': 6,  'i': 0.3, 'a': 0.0},
            {'e': 3, 'e0': 3, 'm': 6, 'i':   0.4, 'a': 0.25}
            ]
    for i, np in enumerate(nation_props):
        np.update({'idx': i, 'r': relations[i], 'd': dist[i], 'die': False})
    nations = [Nation(args=p) for p in nation_props]
    nations = [n.updated(nations) for n in nations]
    initial_state = State(args={'now_player_i': 0, 'players': players, 'nations': nations})
    game = Game(players, initial_state)
    game.run()

