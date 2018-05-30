from game import Game
import pygame
from pygame.locals import *
import numpy as np


class PaintConfig(object):
    class Relation():
        WIDTH = 6
        FRIEND_COLOR = (125, 255, 125)
        EMENY_COLOR = (255, 60, 60)
        def __init__(self, r):
            self.r = r
        @property
        def width(self):
            return int(abs(self.r)*self.WIDTH)
        @property
        def color(self):
            if self.r > 0:
                return self.FRIEND_COLOR
            else:
                return self.EMENY_COLOR
    class Nation():
        def __init__(self, n):
            self.n = n
        def strhash(self, s, seed):
            from functools import reduce

            MOD = 65535
            hash_add = lambda a, b: (a*seed+b) % MOD
            return reduce(hash_add, [ord(c) for c in s+s[::-1]])
        @property
        def size(self):
            return int(self.n.p * 50)
        @property
        def color(self):
            c = np.array([self.strhash(self.n.name, s)%256 for s in [7, 11, 13]])
            return c
        def relation(self, r):
            if abs(r) >= 1:
                return PaintConfig.Relation(r)
            return None

    def __init__(self):
        self.width = 800
        self.height = 600
        self.size = (self.width, self.height)
    def nation(self, nation):
        return PaintConfig.Nation(nation)
    
class GameWithUI(Game):
    class Country():
        def __init__(self, pos):
            self.pos = pos
    def __init__(self, players, initial_state):
        self.pc = PaintConfig()
        pygame.init()
        self.screen = pygame.display.set_mode(self.pc.size)
        d = np.array([n.d for n in initial_state.nations])
        self.nation_pos = self.calc_pos(d)[0]
        self.state = initial_state
    def calc_pos(self, d, margin=0.1, pos=None):
        # Given a distance matrix d, calc pos of all country
        def sqrt(v):
            return np.dot(v.T, v) ** 0.5
        n = len(d)
        t = 50
        flg = lambda x: 1 if x>0 else -1
        p = np.random.rand(n, 2) if pos is None else pos
        ps = []
        rr = [(0.8 * (t-i)/t) ** 2 for i in range(t)]
        for _t in range(t):
            off = np.zeros((n, 2))
            for i in range(n):
                o = np.zeros(2)
                for j in range(n):
                    if i==j: continue
                    diff = sqrt(p[i]-p[j])
                    unit = (p[i]-p[j]) / diff
                    if abs(diff) < 0.1:
                        o += unit * (0.125-abs(diff))
                    from random import random as rnd
                    sq_diff = sqrt(p[i]-p[j]) - d[i][j]
                    o += - 0.3 * (rr[_t]*(rnd()-0.5) + sq_diff) * unit
                off[i] = o
            p = p + off
            p = (p - p.mean(axis=0))
            ps.append(p / p.std(axis=0))

        W, H = self.pc.size
        p = p / p.std(axis=0)
        for i, w in enumerate([W, H]):
            p[:, i] = p[:,i] * w/4 + w/2
            x = p[:, i]
            x[x < 0] = 0
            x[x > w-1] = w-1
        p = p.astype(np.int32)
        return p, ps
    def paint_nation(self):
        for r, n in zip(self.nation_pos, self.state.nations):
            n = self.pc.nation(n)
            pygame.draw.circle(
                    self.screen,
                    n.color, r, n.size, 0)
    def paint_relation(self):
        for i, n1 in enumerate(self.state.nations):
            for j, n2 in enumerate(self.state.nations):
                if i<=j: continue
                r = self.pc.nation(n1).relation(n1.r[j])
                if r is not None:
                    pygame.draw.line(
                            self.screen,
                            r.color,
                            self.nation_pos[i],
                            self.nation_pos[j],
                            r.width)
                
        
    def paint_action(self, act, src, tar):
        pass
    def paint(self, state, player, action_taken):
        pass
    def run(self, n_turns=200):
        for t in range(n_turns):
            p = self.state.now_player
            act = p.action(self.state)
            self.state = self.state.next_turn(p, act)

if __name__=='__main__':
    from time import sleep
    from game import Nation
    class S:
        def __init__(self, ns): self.nations = ns
    d = np.array([ [0,.3,.5,.3], [.3,0,.3,.3], [.5,.3,0,.3], [.3,.3,.3,0] ])
    s = S([Nation(args={
        'd': d[i],
        'p': (i+2)*0.25,
        'r': [1, -1, 0, -2],
        'name': 'nation_'+str(i)
        }) for i in range(4)])
    g = GameWithUI(None, s)
    clock = pygame.time.Clock()
    for _ in range(5):
        for i in range(50):
            clock.tick(20)
            for event in pygame.event.get():
                pass
            g.screen.fill((0,0,0))
            g.paint_relation()
            g.paint_nation()
            pygame.display.flip()

