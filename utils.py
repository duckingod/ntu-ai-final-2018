import enum
# Action = enum.Enum('Action', 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT EXTORT POLICY')
Action = enum.Enum('Action', 'INVADE DENOUNCE MAKE_FRIEND SUPPLY CONSTRUCT POLICY PRODUCE')
INTERACT_ACTIONS = [Action[a] for a in 'INVADE DENOUNCE MAKE_FRIEND SUPPLY'.split()]
SELF_ACTIONS = [Action[a] for a in 'CONSTRUCT POLICY PRODUCE'.split()]

def action_string(act, players):
    if act[0] in SELF_ACTIONS:
        return f"{act[0].name} {act[1] if act[1] is not None else ''}"
    return f"{act[0].name} {players[act[1]].name}"
    str(act if act[0] in SELF_ACTIONS else (act[0], players[act[1]].name))
