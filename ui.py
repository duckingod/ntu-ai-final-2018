from game import Game
import pygame
from pygame.locals import *
import numpy as np
from queue import Queue
import threading
from AIAlgo import Beam, MCTS



class PaintConfig(object):
    class Relation():
        WIDTH = 10
        FRIEND_COLOR = (125, 255, 125)
        EMENY_COLOR = (255, 60, 60)
        def __init__(self, r):
            self.r = r
        @property
        def width(self):
            return int(abs(self.r * 3) ** 2 / 9 * self.WIDTH)
        @property
        def color(self):
            if self.r > 0:
                return self.FRIEND_COLOR
            else:
                return self.EMENY_COLOR
    class Nation():
        def __init__(self, n, name, nations):
            self.n = n
            self.name = name
            self.nations = nations
        def strhash(self, s, seed):
            from functools import reduce

            MOD = 65535
            hash_add = lambda a, b: (a*seed+b) % MOD
            return reduce(hash_add, [ord(c) for c in s+s[::-1]])
        @property
        def size(self):
            mean = sum([_n.e for _n in self.nations]) / len(self.nations)
            return int(self.n.e / mean * 100)
            return int(self.n.p * 50)
        @property
        def color(self):
            c = np.array([self.strhash(self.name, s)%256 for s in [7, 11, 13]])
            if self.n.die:
                c = c * 0.4
            return c
    class Action():
        IMGS = {}
        def __init__(self, act):
            if not act in self.IMGS:
                self.IMGS[act] = pygame.image.load(f"resources/{act}.png")
            self.act = act
        @property
        def image(self):
            return self.IMGS[self.act]

    def __init__(self):
        self.width = 800
        self.height = 600
        self.size = (self.width, self.height)
    def nation(self, *args):
        return PaintConfig.Nation(*args)
    def relation(self, r):
        return PaintConfig.Relation(r)
    def action(self, act):
        return PaintConfig.Action(act)

class GameWithUI(Game):
    class Country():
        def __init__(self, pos):
            self.pos = pos
    def __init__(self, players, initial_state):
        self.pc = PaintConfig()
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 35)
        self.screen = pygame.display.set_mode(self.pc.size)
        d = np.array([n.d for n in initial_state.nations])
        self.nation_pos = self.calc_pos(d)[0]
        self.state = initial_state
        self.players = players
        self.event = Queue()
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
        for i, (r, _n) in enumerate(zip(self.nation_pos, self.state.nations)):
            name = self.players[i].name
            n = self.pc.nation(_n, name, self.state.nations)
            pygame.draw.circle(
                    self.screen,
                    n.color, r, n.size, 0)
            name_color = (230, 230, 230) if i == self.state.now_player_i else (40, 40, 40)
            text = self.font.render(name, True, name_color)
            text_rect = text.get_rect(center=r)
            self.screen.blit(text, text_rect)
    def paint_relation(self):
        for i, n1 in enumerate(self.state.nations):
            for j, n2 in enumerate(self.state.nations):
                if i>=j: continue
                r = self.pc.relation(n1.r[j])
                pygame.draw.line(
                        self.screen,
                        r.color,
                        self.nation_pos[i],
                        self.nation_pos[j],
                        r.width)
    def paint_action(self, act, src, tar):
        img = self.pc.action(act).image
        p_src, p_tar = self.nation_pos[src], self.nation_pos[tar]
        mid = ((p_src + p_tar)/2).astype(np.int32).tolist()
        # img_rect = myimage.get_rect(center=mid)
        # self.screen.blit(img, img_rect)
    def paint_if_human(self):
        if hasattr(self.state.now_player, 'is_human'):
            text = self.font.render('Your turn', True, (200,200,200))
            text_rect = text.get_rect(center=np.array([0.5, 0.9]))
            self.screen.blit(text, text_rect)
    def paint(self):
        self.paint_relation()
        self.paint_nation()
        self.paint_action('invade',0,0)
        self.paint_if_human()
    def run(self, n_turns=200):
        act_str = lambda act: str(act if type(act[1]) is not int or act[1]>=len(self.players) else (act[0], self.players[act[1]].name))
        while True:
            self.event.get()
            p = self.state.now_player
            act = p.action(self.state)
            print(self.state.show())
            self.state = self.state.next_turn(act)
            print('After ' + p.name + ' did ' + act_str(act))
            print(self.state.show())
            print()
            while not self.event.empty():
                self.event.get()

if __name__=='__main__':
    from time import sleep
    from game import Nation
    import init_config

    algo = lambda: Beam(20, 20)
    # algo = lambda: MCTS(turns=15, iter_n=300)
    players, initial_state = init_config.spring(algo)
    game = Game(players, initial_state)

    game = GameWithUI(players, initial_state)
    clock = pygame.time.Clock()
    game_thread = threading.Thread(target=game.run, args=(200,))
    game_thread.start()
    while True:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == QUIT:
                game_thread.exit()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                game.event.put('go go go')
        game.screen.fill((0,0,0))
        game.paint()
        pygame.display.flip()

