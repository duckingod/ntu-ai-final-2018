"""
Place to define effect of actions. (That is, the equations in doc.

To get property of a nation, write
>>> nations[nation_idx].t == NATION_TECH_POWER
Available properties: 'idx', 'die', 'in_war', 'e', 'e0', 'm', 't', 'i', 'a', 'p', 'r', 'd'.
View doc for detail of each property.
   idx: index of this nation
   die: is the nation died


To change a property of a nation, don't assign by `nations[i].t = 10`, please write
>>> nation = nations[i].change({'t': 10})

To confirm a modify of a nation, write the following to pass the result to outside XD
>>> nations[modified_nation_idx] = nations[modified_nation_idx].change({'t': 10})

To change effect, modify `export_effect`

"""

EPS = 0.01


class DefaultEffect():
    @staticmethod
    def invade(nations, src, tar):
        src_n, tar_n = nations[src], nations[tar]
        d = src_n.d[tar]
        ap, dp = src_n.p * (1-0.2*d), tar_n.p
        r = ap / (ap+dp+0.01)
        if ap > dp:
            e_loss = ap * r / 2
            nations[src] = src_n.change({'m': src_n.m - tar_n.m * (1 - r) })
            if tar_n.e - e_loss < tar_n.e0 / 4:
                nations[tar] = tar_n.change({'die': True, 'd': [0] * len(nations), 'm': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
            else:
                nations[tar] = tar_n.change( {'in_war': True, 'm': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
            nations[src] = src_n.change({'in_war': True, 'm': src_n.m - tar_n.m * (1 - r) / d, 'e': src_n.e + e_loss / 2})
        else:
            e_loss = ap * r / 4
            nations[tar] = tar_n.change({'in_war': True, 'm': tar_n.m + tar_n.m * (1 - r)})
            nations[src] = src_n.change({'in_war': True, 'm': src_n.m - tar_n.m * (1 - r) / d})
        nations[tar] = nations[tar].refresh(nations)
        nations[src] = nations[src].refresh(nations)

        
    @staticmethod
    def denounce(nations, src, tar):
        src_n, tar_n = nations[src], nations[tar]
        nations[src] = src_n.change({'r': [r if i!=tar else r - (2-r) * 0.1 for i, r in enumerate(src_n.r)]})
        nations[tar] = tar_n.change({'r': [r - (2 - r) * (0.05 if i!=src else 0.1) for i, r in enumerate(tar_n.r)]})
        nations[tar] = nations[tar].refresh(nations)
        nations[src] = nations[src].refresh(nations)

    @staticmethod
    def make_friend(nations, src, tar):
        src_n, tar_n = nations[src], nations[tar]
        nations[src] = src_n.change({'r': [r if i!=tar else r + (2+r) * 0.1 for i, r in enumerate(src_n.r)]})
        nations[tar] = tar_n.change({'r': [r if i!=src else r + (2+r) * 0.1 for i, r in enumerate(tar_n.r)]})
        nations[tar] = nations[tar].refresh(nations)
        nations[src] = nations[src].refresh(nations)

    @staticmethod
    def supply(nations, src, tar):
        src_n, tar_n = nations[src], nations[tar]
        nations[src] = src_n.change({
            'e': src_n.e - (1 - src_n.a) * src_n.i,
            'r': [r if i!=tar else r + (2+r) * 0.2 for i, r in enumerate(src_n.r)]
            })
        nations[tar] = tar_n.change({
            'e': tar_n.e + (1 - src_n.a) * src_n.i,
            'r': [r if i!=src else r + (2+r) * 0.2 for i, r in enumerate(tar_n.r)]
            })
        nations[tar] = nations[tar].refresh(nations)
        nations[src] = nations[src].refresh(nations)

    @staticmethod
    def produce(nations, src, tar):
        src_n = nations[src]
        nations[src] = src_n.change({
            'e': src_n.e * src_n.growth(_a=0),
            })
        nations[src] = nations[src].refresh(nations)
    @staticmethod
    def extort(nations, src, tar):
        src_n = nations[src]
        nations[src] = src_n.change({
            'e': src_n.e * src_n.growth(a=0),
            'r': [r if i!=tar else r - (2-r) * 0.2 for i, r in enumerate(src_n.r)]
            })
        nations[tar] = tar_n.change({
            'e': tar_n.e - e_loss,
            'r': [r if i!=src else r - (2-r) * 0.2 for i, r in enumerate(tar_n.r)]
            })
        nations[src] = nations[src].refresh(nations)
        nations[tar] = nations[tar].refresh(nations)

    @staticmethod
    def construct(nations, src, _):
        i = nations[src].i
        src_n = nations[src]
        nations[src] = src_n.change({'i': i + 0.1 * ((2-i) if i < 1 else 1)})
        nations[src] = nations[src].refresh(nations)

    @staticmethod
    def policy(nations, src, flag):
        """
        flag: 1 or -1
          - 1 means a += 0.1
          - -1 means a -= 0.1
        """
        src_n = nations[src]
        nations[src] = src_n.change({'a': src_n.a + 0.1 * flag})
        nations[src] = nations[src].refresh(nations)

def invade_v2(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    d = src_n.d[tar]

    ap, dp = src_n.p * (0.3 + 0.7 * d), tar_n.p
    r = ap / (ap+dp+0.01)

    sd = {'in_war': True, 'r': [-1 if i==tar else _r for i, _r in enumerate(src_n.r)]}
    td = {'in_war': True, 'r': [-1 if i==src else _r for i, _r in enumerate(tar_n.r)]}
    if ap > dp:
        e_loss = tar_n.e * r / 2
        if tar_n.e - e_loss < tar_n.e0:
            sd.update({'d': [max(t) for t in zip(src_n.d, tar_n.d)]})
            td.update({'die': True, 'd': [0] * len(nations)})
        else:
            td.update({'m': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        sd.update({'m': src_n.m - tar_n.m * (1 - r), 'e': src_n.e + e_loss})
    else:
        td.update({'m': tar_n.m - src_n.m * r})
        sd.update({'m': src_n.m - src_n.m * (1 - r)})
        m_loss = sd['m'] * (1 - r)
        sd.update({'m': sd['m'] - m_loss})
        td.update({'m': td['m'] + m_loss})
    nations[src] = src_n.change(sd)
    nations[tar] = tar_n.change(td)

def invade_e0(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    d = src_n.d[tar]

    # dr = (0.3 + 0.7 * d)
    dr = d
    ap, dp = src_n.p * dr, tar_n.p
    r = ap / (ap+dp+0.01)

    sd = {'in_war': True, 'r': [-1 if i==tar else _r for i, _r in enumerate(src_n.r)]}
    td = {'in_war': True, 'r': [-1 if i==src else _r for i, _r in enumerate(tar_n.r)]}
    if ap > dp:
        e_loss = tar_n.e * r / 2
        if tar_n.e - e_loss < tar_n.e0 / 4:
            sd.update({'e0': src_n.e0 + tar_n.e0, 'd': [max(t) for t in zip(src_n.d, tar_n.d)]})
            td.update({'die': True, 'd': [0] * len(nations), 'm': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        else:
            td.update({'m': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        sd.update({'m': src_n.m - tar_n.m * (1 - r) / dr, 'e': src_n.e + e_loss * dr})
    else:
        td.update({'m': tar_n.m - src_n.m * r})
        sd.update({'m': src_n.m - src_n.m * (1 - r)})
        m_loss = sd['m'] * (1 - r)
        sd.update({'m': sd['m'] - m_loss / dr})
        td.update({'m': td['m'] + m_loss})
    nations[src] = src_n.change(sd).refresh(nations)
    nations[tar] = tar_n.change(td).refresh(nations)

def invade_e0_easy_die(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    d = src_n.d[tar]

    # dr = (0.3 + 0.7 * d)
    dr = d
    ap, dp = src_n.p * dr, tar_n.p
    r = ap / (ap+dp+0.01)

    sd = {'in_war': True, 'r': [-1 if i==tar else _r for i, _r in enumerate(src_n.r)]}
    td = {'in_war': True, 'r': [-1 if i==src else _r for i, _r in enumerate(tar_n.r)]}
    if ap > dp:
        e_loss = tar_n.e * r / 2
        if tar_n.e - e_loss < tar_n.e0 * 3:
            sd.update({'e0': src_n.e0 + tar_n.e0, 'd': [max(t) for t in zip(src_n.d, tar_n.d)]})
            td.update({'die': True, 'd': [0] * len(nations), 'm': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        else:
            td.update({'m': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        sd.update({'m': src_n.m - tar_n.m * (1 - r) / dr, 'e': src_n.e + e_loss * dr})
    else:
        td.update({'m': tar_n.m - src_n.m * r})
        sd.update({'m': src_n.m - src_n.m * (1 - r)})
        m_loss = sd['m'] * (1 - r)
        sd.update({'m': sd['m'] - m_loss / dr})
        td.update({'m': td['m'] + m_loss})
    nations[src] = src_n.change(sd).refresh(nations)
    nations[tar] = tar_n.change(td).refresh(nations)

def invade_get_e0(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    d = src_n.d[tar]

    # dr = (0.3 + 0.7 * d)
    dr = d
    ap, dp = src_n.p * dr, tar_n.p
    r = ap / (ap+dp+0.01)

    sd = {'in_war': True, 'r': [-1 if i==tar else _r for i, _r in enumerate(src_n.r)]}
    td = {'in_war': True, 'r': [-1 if i==src else _r for i, _r in enumerate(tar_n.r)]}
    if ap > dp:
        e_loss = tar_n.e * r / 2
        e0_loss = tar_n.e0 * r / 3
        if tar_n.e0 - e0_loss < 1:
            sd.update({'e0': src_n.e0 + tar_n.e0, 'd': [max(t) for t in zip(src_n.d, tar_n.d)]})
            td.update({'die': True, 'd': [0] * len(nations), 'm': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss})
        else:
            td.update({'m': tar_n.m - tar_n.m * r, 'e': tar_n.e - e_loss , 'e0': tar_n.e0 - e0_loss})
            sd.update({'e0': src_n.e0 + e0_loss})
        sd.update({'m': src_n.m - tar_n.m * (1 - r) / dr, 'e': src_n.e + e_loss * dr})
    else:
        td.update({'m': tar_n.m - src_n.m * r})
        sd.update({'m': src_n.m - src_n.m * (1 - r)})
        m_loss = sd['m'] * (1 - r)
        sd.update({'m': sd['m'] - m_loss / dr})
        td.update({'m': td['m'] + m_loss})
    nations[src] = src_n.change(sd).refresh(nations)
    nations[tar] = tar_n.change(td).refresh(nations)

def policy_strong(nations, src, flag):
    src_n = nations[src]
    nations[src] = src_n.change({'a': src_n.a + 0.2 * flag})


def denounce_strong(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    nations[src] = src_n.change({'r': [r if i!=tar else r - (1 + r) * 0.5 for i, r in enumerate(src_n.r)]})
    nations[tar] = tar_n.change({'r': [r - (1 + r) * (0.25 if i!=src else 0.5) for i, r in enumerate(tar_n.r)]})
    nations[tar] = nations[tar].refresh(nations)
    nations[src] = nations[src].refresh(nations)

def make_friend_strong(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    nations[src] = src_n.change({'r': [r if i!=tar else r + (2-r) * 0.4 for i, r in enumerate(src_n.r)]})
    nations[tar] = tar_n.change({'r': [r if i!=src else r + (2-r) * 0.4 for i, r in enumerate(tar_n.r)]})
    nations[tar] = nations[tar].refresh(nations)
    nations[src] = nations[src].refresh(nations)

def supply_strong(nations, src, tar):
    src_n, tar_n = nations[src], nations[tar]
    e_trans = src_n.e - src_n.e / src_n.growth()
    nations[src] = src_n.change({
        'e': src_n.e - e_trans,
        'r': [r if i!=tar else r + (1+r) * 0.7 for i, r in enumerate(src_n.r)]
        })
    nations[tar] = tar_n.change({
        'e': tar_n.e + e_trans,
        'r': [r if i!=src else r + (1+r) * 0.7 for i, r in enumerate(tar_n.r)]
        })
    nations[tar] = nations[tar].refresh(nations)
    nations[src] = nations[src].refresh(nations)

export_effect = {
        'invade': DefaultEffect.invade,
        'denounce': DefaultEffect.denounce,
        'make_friend': DefaultEffect.make_friend,
        'supply': DefaultEffect.supply,
        'construct': DefaultEffect.construct,
        'extort': DefaultEffect.extort,
        'produce': DefaultEffect.produce,
        'policy': DefaultEffect.policy
        }

export_effect['invade'] = invade_v2
export_effect['invade'] = invade_e0
export_effect['invade'] = invade_e0_easy_die
export_effect['invade'] = invade_get_e0

export_effect['policy'] = policy_strong 
export_effect['supply'] = supply_strong
export_effect['make_friend'] = make_friend_strong
export_effect['denounce'] = denounce_strong
