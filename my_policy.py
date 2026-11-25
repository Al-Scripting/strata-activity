"""Part 2: your agent. Fill in the two TODOs below, then run:  python grade.py

Every day the game calls pick(view), and the party walks to the place you return. It must be one
of view.neighbors. This is the route network's job from the lecture: given what the party knows,
where next?

What view gives you (the details are in quest.py):
  view.here            where the party is
  view.neighbors       the places you can walk to today
  view.level, view.exp, view.exp_next, view.items, view.day, view.days_left
  view.known           {name: PlaceInfo} for every place you have seen. A PlaceInfo has
                       .name .kind .level .visited .cleared
                       .ok          True when the party can enter it right now
                       .blocked_by  why not, e.g. ["item:Crown", "level:10"]
                       .gives       its key items (None until you have got them)
                       .exp         EXP per visit (None until you have been there)
  view.final           the name of the last boss once you have seen it, else None
  view.path_to(name)   the shortest safe path [next step, ..., name], or None
  view.last            what happened yesterday

Watch your agent play:  python run.py --map ff1 --show
"""
from baselines import farm


class Policy:
    def __init__(self):
        pass                      # a new Policy is made for every map: keep memory in self

    def pick(self, view):
        # Step 1. EXPLORE: list the places worth going to (slide "How the route network chooses").
        #         Worth going to = a place you have not visited yet,
        #                       or a story place ("dungeon", "event", "gate") you have not cleared.
        targets = []
        for p in view.known.values():
            if p.name == view.here or not p.ok:
                continue          # skip where you are, and places you cannot enter yet
            # TODO 1: if p is worth going to, add it:  targets.append(p)
            #         Hint: p.visited, p.kind and p.cleared tell you what you need.

        # Step 2. Keep the ones you can walk to, and go to the nearest.
        # TODO 2: delete the "# " (hash and space) at the start of the 4 lines below.
        #         In VS Code: select the 4 lines and press Ctrl+/ (Cmd+/ on a Mac).
        # reachable = [p for p in targets if view.path_to(p.name)]
        # if reachable:
        #     best = min(reachable, key=lambda p: len(view.path_to(p.name)))
        #     return view.path_to(best.name)[0]

        # Step 3. Nothing worth visiting? The party is too weak for the next boss, so grind for
        #         EXP and come back stronger (slide "Progress over the run"). farm() does it.
        return farm(view)
