class Nation(object):
    """
    >>> n = Nation(args={'p':123, 'a':0.5, 'r':[0, -1, 1, None, 1]})
    >>> new_n = Nation(n) # Copy nation
    """
    PARAMS = ['a', 'p', 'r', 'd', 'name']
    def __init__(self, n=None, args={}):
        if n is not None:
            for p in self.PARAMS:
                setattr(self, p, self.clone(getattr(n, p)))
        for p, v in args.items():
            setattr(self, p, self.clone(v))
    def __repr__(self):
        return 'Nation: ' + {p:getattr(self, p) for p in self.PARAMS}.__repr__()
    def __str__(self):
        return 'Nation: ' + {p:getattr(self, p) for p in self.PARAMS}.__str__()
    def clone(self, o):
        if type(o) is dict:
            return {k: self.clone(v) for k, v in o.items()}
        elif type(o) is list:
            return [self.clone(v) for v in o]
        return o
    @property
    def m(self):
        return (1-self.a) * self.p

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
    def __init__(self, players, now_player_i, nations):
        """
        args
            players(list): list of player object
            now_player_i(int): index of player who can take action
            nations(dict): key: player_i, value: Nation object
        """
        self.players = players
        self.now_player_i = now_player_i
        self.nations = nations
    @property
    def now_player(self):
        """
        return: 現在該動作的 player
        """
        return self.players[self.now_player_i]
    def next_turn(self, action):
        """
        compute new state object by now_player and given action.
        should not change state of self.
        args
            action(tuple): (action_name, action_param) the action that now_player takes.
        returns
            new_state
        """
        
        nations = self.nations
        """doing action to update nations"""
        if action[0] == "invade":
            pass
        elif action[0] == "denounce":
            pass
        elif action[0] == "make_friend":
            pass
        elif action[0] == "supply":
            pass
        elif action[0] == "construct":
            pass
        
        now_player_i_next = (self.now_player_i + 1) % len(self.players)
        new_state = State(self.players, now_player_i_next, nations)
        """nations needs to update by taking action above"""
        return new_state
        
        
        
    def actions(self):
        """
        Avaliable actions for now_player
        """
        pass
    
    def update(self):
        pass
        
class Game:
    '''
    (／‵Д′)／~ ╧╧
    '''
    def __init__(self, players, initial_state):
        raise NotImplementedError("To be implemented ?!")
    def run(self, n_turns=200):
        for t in range(n_turns):
            p = self.state.now_player
            act = p.action(self.state)
            self.state = self.state.next_turn(p, act)

class Player:
    @property
    def name(self):
        raise NotImplementedError("To be implemented 好神")
    def h(self, state, action_taken=None):
        raise NotImplementedError("To be implemented duckingod")
    def action(self, state):
        raise NotImplementedError("To be implemented QAQ")

if __name__=='__main__':
    from ai import AIPlayer, Beam
    players = [
        AIPlayer('Alpha', Beam()),
        AIPlayer('Beta', Beam())
        ]
    initial_state = State()
    game = Game(players, initial_state)
    game.run()

