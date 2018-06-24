from math import log

from utils import Action

def extract(f):
    def _e(player, state, last_action):
        src = player.idx
        n = state.nations[src]
        if state.last_state:
            action, tar = state.last_state.performed_action
        else:
            action, tar = None, None
        return f(state, n, action, src, tar)
    return _e

def sn(player, state):
    return state[player.idx]

@extract
def died(state, n, action, src, tar):
    return -1000000 if n.die else 0

def common(a, p):
    @extract
    def _common(state, n, action, src, tar):
        power = n.m + (n.p - n.m) * 0.5
        # power = n.m
        if p=='f':
            return log(n.e + power + 0.1)
        if p=='m':
            return log(n.e + power + 0.1) + log(power + 0.1)
        if p=='b':
            return log(n.e + 0.1)
        if p=='old':
            return n.e + n.m
        raise Exception('Unknown personality: ' + p)
    return _common

def invade(a, p):
    @extract
    def _invade(state, n, action, src, tar):
        if action == Action.INVADE:
            n = state.last_state.nations[src]
            return -a * n.d[tar] * (n.r[tar] - love)
        return 0
    if p == '':
        love = 0
    elif p == 'love':
        love = 1
    elif p == 'hate':
        love = -1
    else:
        raise Exception('Unknown personality: ' + p)
    return _invade

def diplomatic(a, p):
    @extract
    def _dip(state, n, action, src, tar):
        if p=='lnh':
            return a * sum([abs(r) for r in n.r])
        if p=='mod':
            return a * sum([    r  for r in n.r])
        if p=='island':
            return a * sum([d * r  for r, d in zip(n.r, n.d)])
        if p=='tao':
            return 0
        raise Exception('Unknown personality: ' + p)
    return _dip

def love_union(a, p):
    @extract
    def _dip(state, n, action, src, tar):
        is_die = lambda n: not n.die
        if p=='':
            return 0
        elif p=='love':
            return - a * len(list(filter(is_die, state.nations)))
        elif p=='hate':
            return a * len(list(filter(is_die, state.nations)))
        raise Exception('Unknown personality: ' + p)
    return _dip

def potential(a, p):
    @extract
    def po(state, n, action, src, tar):
        return a * (n.t / n.i)
    return po

def get_h(personality=['f', '', 'tao', 'love', ''], params=[None, 0.5, 1, 10, 1]):
    fs = [common, invade, diplomatic, love_union, potential]
    fs = [f(a, p) for f, p, a in zip(fs, personality, params)]
    fs.append(died)
    def compute(player, state, action):
        return sum([f(player, state, action) for f in fs])
    return compute

