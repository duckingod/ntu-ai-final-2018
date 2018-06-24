from game import Game
import pygame
from pygame.locals import *
import numpy as np
from queue import Queue
import threading
from AIAlgo import Beam, MCTS
from utils import Action, INTERACT_ACTIONS, SELF_ACTIONS
import utils



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
        SIZE = 100
        ALPHA = 200
        SURFACE = pygame.Surface((SIZE * 4, SIZE * 4))
        def __init__(self, n, name, nations):
            self.n = n
            self.name = name
            self.nations = nations
            self.region = pygame.Surface((self.size, self.size))
            self.region.set_colorkey((0,0,0))
            self.region.set_alpha(self.ALPHA)
            mid = (self.size // 2, self.size // 2)
            pygame.draw.circle(self.region, self.color, mid, self.size // 2)
            pygame.draw.circle(self.region, (255, 50, 50), mid, self.m_size // 2)
        def strhash(self, s, seed):
            from functools import reduce

            MOD = 65535
            hash_add = lambda a, b: (a*seed+b) % MOD
            return reduce(hash_add, [ord(c) for c in s+s[::-1]])
        @property
        def size(self):
            mean = sum([_n.e for _n in self.nations]) / len(self.nations)
            return int(self.n.e / mean * self.SIZE)
        @property
        def m_size(self):
            return int(self.size * (self.n.m / self.n.e)) 
        @property
        def color(self):
            c = np.array([self.strhash(self.name, s)%256 for s in [7, 11, 13]])
            if self.n.die:
                c = c * 0.4
            return c
    class Action():
        IMGS = {}
        def __init__(self, act):
            act = act.name.lower()
            if not act in self.IMGS:
                img = pygame.image.load(f"resources/{act}.png")
                img = pygame.transform.scale(img, (50, 50))
                self.IMGS[act] = img
            self.act = act
        @property
        def image(self):
            return self.IMGS[self.act]

    def __init__(self):
        self.width = 800
        self.height = 600
        self.size = (self.width, self.height)
        bg = pygame.image.load(f"resources/background.png")
        bg = pygame.transform.scale(bg, self.size)
        self.background = bg
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
    def __init__(self, players, initial_state, nation_position=None):
        super().__init__(players, initial_state)
        self.pc = PaintConfig()
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 35)
        self.screen = pygame.display.set_mode(self.pc.size)
        d = np.array([n.d for n in initial_state.nations])
        self.nation_pos = self.calc_pos(d, pos=nation_position)[0]
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
                    sq_diff = sqrt(p[i]-p[j]) - (1.5-d[i][j])
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
            self.screen.blit(n.region, n.region.get_rect(center=r))
            name_color = (40, 40, 40)
            name_str = name
            if i == self.state.now_player_i:
                name_color = (230, 230, 230) 
                name_str = '>> ' + name_str + ' <<'
            if self.state.last_state and i == self.state.last_state.now_player_i:
                name_color = (180, 180, 180) 
            text = self.font.render(name_str, True, name_color)
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
        pos = tar if act in INTERACT_ACTIONS else src
        pos = self.nation_pos[pos].astype(np.int32).tolist()
        pos[1] += 40
        img_rect = img.get_rect(center=pos)
        self.screen.blit(img, img_rect)
    def paint_bg(self):
        self.screen.blit(self.pc.background, (0, 0))
    def paint_if_human(self):
        if hasattr(self.state.now_player, 'is_human'):
            text = self.font.render('Your turn', True, (200,200,200))
            text_pos = np.array([0.5 * self.pc.size[0], 0.9 * self.pc.size[1]])
            text_rect = text.get_rect(center=text_pos)
            self.screen.blit(text, text_rect)
    def paint(self):
        def last_act():
            if self.state.last_state:
                ls = self.state.last_state
                act, tar = ls.performed_action
                if act:
                    return act, ls.now_player_i, tar
            return None
        self.paint_bg()
        self.paint_relation()
        self.paint_nation()
        if last_act():
            self.paint_action(*last_act())
        self.paint_if_human()
    def run(self, n_turns=200):
        while True:
            self.event.get()
            p = self.state.now_player
            act = p.action(self.state)
            print(self.state.show())
            self.state = self.state.next_turn(act)
            print('After ' + p.name + ' did ' + utils.action_string(act, self.players))
            print(self.state.show())
            print()
            while not self.event.empty():
                self.event.get()
    def start_flow(self):
        from time import sleep
        clock = pygame.time.Clock()
        game_thread = threading.Thread(target=self.run, args=(200,))
        game_thread.start()
        while True:
            clock.tick(300)
            for event in pygame.event.get():
                if event.type == QUIT:
                    game_thread.exit()
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    self.event.put('go go go')
            self.paint()
            pygame.display.flip()

if __name__=='__main__':
    import init_config

    # algo = lambda: Beam(20, 20)
    algo = lambda: MCTS(turns=15, iter_n=300)
    players, initial_state = init_config.spring(algo)
    # 'QIN' 'HAN' 'ZHAO' 'WEI'
    start_pos = np.array([(-1, 0), (0, 0), (0, -1), (0, -0.5)])
    game = GameWithUI(players, initial_state, start_pos)
    game.start_flow()

