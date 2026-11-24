"""Your agent. Edit this file.

Task 1, answer here in two sentences: why does baselines.KeyChaser get stuck on the FF1 map?
    (your answer)

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
      python run.py                       (your score on all 31 test maps)
"""
from baselines import farm


class Policy:
    def __init__(self):
        pass

    def pick(self, view):
        # Step 1. Make a list of places worth going to. A good start: places you can enter
        # (p.ok) that you have not visited yet, and story places (dungeon, event, gate) you
        # have not cleared. Skip view.here.
        targets = []
        for p in view.known.values():
            if p.name == view.here or not p.ok:
                continue
            # TODO: append p to targets when it is new or an uncleared story place

        # Step 2. Keep only the ones you can walk to: view.path_to(p.name) is not None.
        # Step 3. Go to the nearest one: return view.path_to(best.name)[0]
        # TODO: steps 2 and 3

        # Step 4. Nothing worth visiting? You are too weak for the next boss: farm EXP.
        return farm(view)
