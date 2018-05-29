class AIPlayer(player):
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
    def __init__(self, ai_name, algo):
        self.ai_name = ai_name
        self.algo = algo
    @property
    def name(self):
        return 'CPU:'+self._name
    def action(self, state):
        return self.algo.get_action(self, state)

class AIAlgo:
    def get_action(self, player, state):
        raise NotImplementedError("To be implemented (´・ω・`)")

class Beam(AIAlgo):
    '''
    (*ﾟ∀ﾟ*)
    duckingod
    RRRRRRRRR
    da'shen'hao'shen
    '''
    def __init__(self, topk=50, turns=50):
        self.topk = topk
        self.turns = turns
    def get_action(self, player, state):
        from itertools import chain
        chain = lambda l: list(chain.from_iterable(l))
        states = [(state.next_turn(a), None, a) for a in state.actions() ]
        for i in range(self.turns):
            p = states[0].now_player
            states = chain([[(s.next_turn(a), a, original_a) for a in s.actions()] for s, _, original_a in states])
            states = states.sort(key=lambda s: -p.h(s[0], s[1]))[:self.topk]
        return max(states, key=lambda s: player.h(s))[2]

