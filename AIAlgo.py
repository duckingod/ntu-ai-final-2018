import random

from itertools import chain as original_chain
def chain(l):
    return list(original_chain.from_iterable(l))

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
        player_i = state.now_player_i
        n_player = len(state.players)
        for i in range(self.turns // n_player):
            for j in range(1, n_player): # 1 because state of this player has been expanded above
                now_player = state.players[(player_i + j) % n_player]
                new_states, pass_states = [], []
                for s, _, original_a in states:
                    if s.now_player == now_player:
                        new_states.append([(s.next_turn(a), a, original_a) for a in s.actions()])
                    else:
                        pass_states.append((s, None, original_a))
                new_states = chain(new_states)
                new_states.sort(key=lambda s: -now_player.h(s[0], s[1]))
                # make 'passed turn' be in top k
                # that is, maintain he 'cannot do anything and pass the turn'
                states = (pass_states + new_states)[:self.topk]
        return max(states, key=lambda s: player.h(s[0], s[2]))[2] # Bug! s[2] is not correct QQ
class MCTS(AIAlgo):
    class mcts_node(object):
        def __init__(self, total_score=3, visit_n=1, state=None, parent=None, player=None, parent_action=None):
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
    def __init__(self, turns=15, iter_n=999):
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
            node = max(node.child_nodes, key=lambda child_node: ( (0+child_node.total_score) / child_node.visit_n) )
        return node
    def expansion(self, node):
        node.child_nodes = [ self.mcts_node(state=node.state.next_turn(a), parent=node, player=node.state.next_turn(a).now_player, parent_action=a) for a in node.state.actions() ]    
        return node.child_nodes[0]
    def simulation(self, node):
        state = node.state
        for i in range(self.turns):
            state = state.next_turn(random.choice(state.actions()))
            # print(state.nations[state.now_player_i])
        return state
    def backpropagation(self, state, node):
        while node.parent:
            """FIXME"""
            node.total_score += node.parent.player.h(state, None) / self.dict_player_init_h[node.parent.player.idx] #""" what is h look like???"""
            node.visit_n += 1
            node = node.parent
        return None
    def get_action(self, state):
        self.root = self.mcts_node(state=state, parent=None, player=state.now_player, parent_action=None)
        self.dict_player_init_h = {player.idx:player.h(state, None) for player in state.players }
        # print(self.dict_player_init_h)
        # [player.h(player, state) for player in state.players]
        for i in range(self.iter_n):
            # print(i)
            # print(self.root.player.idx)
            # for child_node in self.root.child_nodes:
                # print(child_node.visit_n)
            #    print((0+child_node.total_score) / child_node.visit_n)
            node_select= self.selection(self.root)
            node_new = self.expansion(node_select)
            state_final = self.simulation(node_new)
            self.backpropagation(state_final, node_new)
        node_best = max(self.root.child_nodes, key=lambda child_node: child_node.total_score / child_node.visit_n)
        return node_best.parent_action
        """
        if lose is doomed, AI may be wrong
        """
