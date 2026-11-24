"""Your route policy. Edit this file.

Each day the game calls pick(view) and walks the party to the place you return. It must be one of
view.neighbors. A new Policy is made for every map, so you can keep memory in self.

What view gives you (see quest.py for the details):
  view.here            where the party is
  view.neighbors       the places you can walk to today
  view.level, view.exp, view.exp_next, view.items, view.day, view.days_left
  view.known           {name: PlaceInfo} for every place you have seen. A PlaceInfo has
                       .kind .level .needs .after .visited .cleared
                       .gives       (None until you have got it)
                       .blocked_by  e.g. ["item:Crown", "level:10"]; [] means you can enter
                       .ok          True when blocked_by is empty
                       .links       the roads you know from it
  view.final           the name of the last boss once you have seen it, else None
  view.path_to(name)   the shortest known safe path [next step, ..., name], or None
  view.last            what happened yesterday

Run:  python run.py --map ff1 --show      (watch one map, day by day)
      python run.py                       (your score on all test maps)
"""
from baselines import farm


class Policy:
    def __init__(self):
        pass

    def pick(self, view):
        # TODO: a better rule. This starter only farms, so it never finishes a map.
        return farm(view)
