"""quest.py: a small quest map in the style of FINAL FANTASY (1987), for the STRATA route challenge.

The party stands on one place. Every day your policy picks one neighbouring place and the party
walks there. What happens depends on the kind of place:

  town     Safe. After a wipe the party wakes up in the last town it visited.
  field    10 random battles: the party earns EXP.
  dungeon  10 battles, plus a boss and key items the first time.
  event    Someone who trades: bring the key items they need and they hand over new ones.
  gate     A boss. It turns the party away until it holds the key items AND has the level.
           Beating the final gate wins the map.

The numbers are FINAL FANTASY's: the EXP table and every place's EXP come from the NES game (via
Disch's disassembly), and boss levels from RPGSite's FF1 boss guide. See README.md.

Any place can also need key items (a port needs the ship) or other places cleared first. Without
them the party is turned away: it stays where it was and the day is lost. A party below the level
of a field or dungeon is wiped: back to the last town, and 3 days are lost.

Fog of war: you see only places you have visited and their neighbours, and you learn what a place
gives only after you get it.
"""
import json
import os
import random
from collections import deque

WIPE_DAYS = 3
BATTLES_PER_VISIT = 10
HERE = os.path.dirname(os.path.abspath(__file__))
# EXP a character needs to reach each level (index = level), FINAL FANTASY (NES)
EXP_TO_REACH = [0, 0, 40, 196, 547, 1171, 2146, 3550, 5461, 7957, 11116, 15016, 19735, 25351, 31942, 39586,
                48361, 58345, 69617, 82253, 96332, 111932, 129131, 148008, 168639, 191103, 215479, 241843,
                270275, 300851, 333651, 366450, 399250, 432049, 464849, 497648, 530448, 563247, 596047,
                628846, 661646, 694445, 727245, 760044, 792844, 825643, 858443, 891242, 924042, 956841, 989641]


def level_for(exp):
    """The level a character with this much EXP has (1 to 50)."""
    level = 1
    while level < 50 and exp >= EXP_TO_REACH[level + 1]:
        level += 1
    return level


def battle_exp(place_level):
    """Mean EXP of one battle at a place of this level. FF1's areas fit about 6 x level² (generated
    maps use this; the FF1 map has each place's real number)."""
    return 6 * max(1, place_level) ** 2


class Place:
    """exp: EXP each character gets per visit (the battles' EXP is shared by the 4 characters).
    boss_exp: EXP each character gets for the boss, the first time only."""

    def __init__(self, name, kind, level=0, needs=(), after=(), gives=(), exp=None, boss_exp=None):
        self.name, self.kind, self.level = name, kind, level
        self.needs, self.after, self.gives = tuple(needs), tuple(after), tuple(gives)
        fights = kind in ("field", "dungeon", "gate")
        self.exp = exp if exp is not None else (BATTLES_PER_VISIT * battle_exp(level) // 4 if fights else 0)
        self.boss_exp = boss_exp if boss_exp is not None else (45 * level if kind in ("dungeon", "gate") else 0)
        self.links = []


class Quest:
    """One map being played. Policies never touch this: they get a View each day."""

    def __init__(self, places, links, start, final, days, title="map"):
        self.places = {p.name: p for p in places}
        for a, b in links:
            self.places[a].links.append(b)
            self.places[b].links.append(a)
        self.start, self.final, self.days, self.title = start, final, days, title
        self.reset()

    @classmethod
    def load(cls, name):
        """A map file from maps/ (e.g. "ff1"), or a generated map ("seed:7")."""
        if name.startswith("seed:"):
            return generate(int(name[5:]))
        path = name if name.endswith(".json") else os.path.join(HERE, "maps", name + ".json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        places = [Place(p["name"], p["kind"], p.get("level", 0), p.get("needs", ()), p.get("after", ()),
                        p.get("gives", ()), p.get("exp"), p.get("boss_exp")) for p in d["places"]]
        return cls(places, d["links"], d["start"], d["final"], d["days"], d.get("title", name))

    def reset(self):
        self.here = self.town = self.start
        self.day, self.level, self.exp = 0, 1, 0
        self.items, self.cleared, self.got = set(), set(), set()
        self.visited = {self.start}
        self.won = False
        self.last = f"The party sets out from {self.start}."

    @property
    def over(self):
        return self.won or self.day >= self.days

    def blocked_by(self, name):
        """Why the party cannot safely enter this place now ([] = it can)."""
        p = self.places[name]
        out = [f"item:{i}" for i in p.needs if i not in self.items]
        out += [f"after:{a}" for a in p.after if a not in self.cleared]
        if p.kind in ("field", "dungeon", "gate") and name not in self.cleared and self.level < p.level:
            out.append(f"level:{p.level}")
        return out

    def _gain(self, exp):
        self.exp += exp
        self.level = max(self.level, level_for(self.exp))

    def _clear(self, p):
        self.cleared.add(p.name)
        if p.name not in self.got:
            self.got.add(p.name)
            self.items.update(p.gives)
            return " Got: " + ", ".join(p.gives) + "." if p.gives else " Nothing to take here."
        return ""

    def move(self, name):
        """Walk to a neighbouring place for one day. Returns what happened."""
        if self.over:
            raise RuntimeError("the map is over")
        p = self.places.get(name)
        if p is None or name not in self.places[self.here].links:
            raise ValueError(f"{name!r} is not a neighbour of {self.here!r}; "
                             f"pick one of {self.places[self.here].links}")
        self.day += 1
        lacking = [b for b in self.blocked_by(name) if not b.startswith("level")]
        if lacking or (p.kind == "gate" and self.blocked_by(name)):
            self.last = f"{name} turns the party away ({', '.join(self.blocked_by(name))})."
            return self.last
        if p.kind in ("field", "dungeon") and self.level < p.level:
            self.day += WIPE_DAYS
            self.here = self.town
            self.last = f"Wiped in {name} (LV {self.level} < {p.level})! Back to {self.town}."
            return self.last
        self.here = name
        self.visited.add(name)
        msg = f"Reached {name}."
        if p.kind == "town":
            self.town = name
            msg += self._clear(p) if p.gives else ""
            self.cleared.add(name)
        elif p.kind == "field":
            self._gain(p.exp)
            msg += f" Battles: +{p.exp} EXP each."
        elif p.kind == "dungeon":
            gain = p.exp + (p.boss_exp if name not in self.got else 0)
            self._gain(gain)
            msg += f" Battles: +{gain} EXP each." + self._clear(p)
        elif p.kind == "event":
            msg += self._clear(p)
        elif p.kind == "gate":
            if name not in self.cleared:
                gain = p.exp + p.boss_exp
                self._gain(gain)
                msg += f" Boss beaten: +{gain} EXP each." + self._clear(p)
            if name == self.final:
                self.won = True
                msg += " The map is won!"
        self.last = msg
        return msg

    def view(self):
        return View(self)


class PlaceInfo:
    """What the party knows about one place."""

    def __init__(self, q, name):
        p = q.places[name]
        self.name, self.kind, self.level = name, p.kind, p.level
        self.needs, self.after = p.needs, p.after
        self.visited = name in q.visited
        self.cleared = name in q.cleared
        self.gives = p.gives if name in q.got else None       # None = not known yet
        self.blocked_by = q.blocked_by(name)                  # e.g. ["item:Crown", "level:10"]
        self.ok = not self.blocked_by                         # safe to enter right now
        # roads are known when one end has been visited
        self.links = [n for n in p.links if self.visited or n in q.visited]

    def __repr__(self):
        state = "cleared" if self.cleared else "visited" if self.visited else "seen"
        return f"<{self.kind} {self.name!r} LV{self.level} {state} blocked_by={self.blocked_by}>"


class View:
    """Everything your policy may read on one day. Read-only: changing it changes nothing."""

    def __init__(self, q):
        self.here = q.here
        self.day, self.days_left = q.day, q.days - q.day
        self.level, self.exp = q.level, q.exp                # EXP of each character, in total
        self.exp_next = EXP_TO_REACH[min(q.level + 1, 50)]   # total EXP needed for the next level
        self.items = set(q.items)
        self.neighbors = list(q.places[q.here].links)
        names = set(q.visited) | {n for v in q.visited for n in q.places[v].links}
        self.known = {n: PlaceInfo(q, n) for n in names}
        self.final = q.final if q.final in names else None   # the last boss, once seen
        self.last = q.last                                   # what happened yesterday

    def path_to(self, target, safe=True):
        """Shortest known path [next step, ..., target], or None. With safe=True the path only
        walks through places the party can enter right now (the target itself may be blocked)."""
        prev, todo = {self.here: None}, deque([self.here])
        while todo:
            u = todo.popleft()
            if u == target:
                break
            if u != self.here and safe and not self.known[u].ok:
                continue                                     # cannot walk through it
            for v in self.known[u].links:
                if v not in prev:
                    prev[v] = u
                    todo.append(v)
        if target not in prev or target == self.here:
            return None
        path = [target]
        while prev[path[-1]] != self.here:
            path.append(prev[path[-1]])
        return path[::-1]


def play(policy, quest, show=False):
    """Run one policy on one map until it is won or out of days. Returns the quest."""
    quest.reset()
    if show:
        print(f"== {quest.title}: {len(quest.places)} places, {quest.days} days ==")
    while not quest.over:
        view = quest.view()
        choice = policy.pick(view)
        msg = quest.move(choice)
        if show:
            print(f"day {quest.day:3}  LV {quest.level:2}  {quest.here:<22} {msg}")
    return quest


# ---------------------------------------------------------------- random maps
TOWNS = ["Ashford", "Brinehold", "Calder", "Dunmere", "Eastmarch", "Fallow", "Gildenport", "Harrowgate",
         "Ironwell", "Juniper", "Kestrel", "Lowmoor", "Mistral", "Northcairn", "Oakhaven", "Pellmar"]
FIELDS = ["Plains", "Moor", "Steppe", "Woods", "Shoals", "Heath", "Downs", "Fen"]
DUNGEONS = ["Cave", "Tower", "Crypt", "Mine", "Ruins", "Grotto", "Keep", "Sewers"]
EVENTS = ["Hermit", "Sage", "Smith", "Witch", "Oracle", "Ferryman", "Scholar", "Chief"]
BOSSES = ["Golem", "Hydra", "Lich", "Wyvern", "Kraken", "Chimera", "Titan", "Phoenix"]
ITEMS = ["Key", "Map", "Bell", "Lens", "Seal", "Horn", "Feather", "Lantern", "Crown", "Ring", "Orb", "Scroll"]
METALS = ["Iron", "Silver", "Old", "Jade", "Ruby", "Glass", "Star", "Moon"]


def generate(seed):
    """A random map: 4 to 6 regions, each with a town, a field, a chain of key items and a boss
    gate whose reward opens the next region. Some regions hide the gate behind a second town, and
    some have a place that wants a key item and gives nothing back."""
    rng = random.Random(seed)
    regions = rng.randint(4, 6)
    used = set()

    def name(pool, extra=None):
        while True:
            n = rng.choice(pool) if extra is None else f"{rng.choice(extra)} {rng.choice(pool)}"
            if n not in used:
                used.add(n)
                return n

    def town_name():
        return name(TOWNS)

    def item():
        return name(ITEMS, METALS)

    places, links = [], []

    def add(p, *to):
        places.append(p)
        links.extend((p.name, t.name) for t in to)
        return p

    gate_level, opener, prev_town, start, prev_spots, final = 1, (), None, None, [], None
    for r in range(regions):
        field_level = 1 if r == 0 else gate_level
        gate_level = field_level + rng.randint(3, 6)
        town = add(Place(town_name(), "town", needs=opener), *([prev_town] if prev_town else []))
        start = start or town.name
        field = add(Place(f"{town.name} {rng.choice(FIELDS)}", "field", field_level), town)
        spots, have = [town, field], opener
        for _ in range(rng.randint(1, 3)):                    # the key-item chain of this region
            gives = (item(),)
            if rng.random() < 0.5:
                lv = rng.randint(field_level, gate_level)
                p = Place(f"{name(DUNGEONS, METALS)}", "dungeon", lv, needs=have, gives=gives)
            else:
                p = Place(f"{town.name} {name(EVENTS)}", "event", needs=have, gives=gives)
            spots.append(add(p, rng.choice(spots)))
            have = gives
        if rng.random() < 0.5:                                # the gate sits behind a second town
            outpost = add(Place(town_name(), "town", needs=opener), rng.choice(spots))
            spots.append(outpost)
            at = outpost
        else:
            at = rng.choice(spots[1:])
        last = r == regions - 1
        gate = add(Place(f"{name(BOSSES)} of {town.name}", "gate", gate_level, needs=have,
                         gives=() if last else (item(),)), at)
        if rng.random() < 0.6:                                # a trap: wants an item, gives nothing
            add(Place(f"{name(DUNGEONS, METALS)} Shrine", "event", needs=rng.choice([have, opener or have])),
                rng.choice(spots))
        if r and rng.random() < 0.5:                          # a loop back to the last region
            links.append((rng.choice(spots).name, rng.choice(prev_spots).name))
        opener, prev_town, prev_spots, final = gate.gives, town, spots, gate.name
    links = list({tuple(sorted(e)) for e in links if e[0] != e[1]})
    days = 150 * regions
    return Quest(places, links, start, final, days, title=f"seed:{seed}")
