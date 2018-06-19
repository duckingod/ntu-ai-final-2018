from math import log

from utils import Action

def extract(f):
    def _e(player, state, last_action):
        src = player.idx
        n = state.nations[src]
        action, tar = last_action
        return f(state, n, action, src, tar)
    return _e

def sn(player, state):
    return state[player.idx]

def h_template(player, state, last_action):
    return self._h(self, state, last_action)

@extract
def died(state, n, action, src, tar):
    return -1000000000 if n.die else 0

def common(a, p):
    @extract
    def _common(state, n, action, src, tar):
        if p=='f':
            return log(n.e + n.m)
        if p=='m':
            return log(n.e) + log(n.m)
        if p=='b':
            return log(n.e)
        if p=='old':
            return n.e + n.m
        raise Exception('Unknown personality: ' + p)
    return _common

def invade(a, p):
    @extract
    def _invade(state, n, action, src, tar):
        if action == Action.INVADE:
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


def get_h(personality=['f', '', 'tao'], params=[None, 0.5, 1]):
    fs = [common, invade, diplomatic]
    fs = [f(a, p) for f, p, a in zip(fs, personality, params)]
    fs.append(died)
    def compute(player, state, action):
        return sum([f(player, state, action) for f in fs])
    return compute

