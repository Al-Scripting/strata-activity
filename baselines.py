"""Two simple policies to compare against. Read them: they show how to use the View."""
import random


class RandomWalk:
    """Picks a random neighbour every day."""

    def __init__(self):
        self.rng = random.Random(0)

    def pick(self, view):
        return self.rng.choice(view.neighbors)


class KeyChaser:
    """Goes to the nearest known story place (dungeon, event or gate) it can enter and has not
    cleared. With none in sight it farms the strongest field or dungeon it can survive.

    A greedy rule that never explores. Run it on the FF1 map with --show and watch where it stops
    making progress, then work out why."""

    def pick(self, view):
        story = [p for p in view.known.values()
                 if p.kind in ("dungeon", "event", "gate") and not p.cleared and p.ok
                 and view.path_to(p.name)]
        if story:
            target = min(story, key=lambda p: len(view.path_to(p.name)))
            return view.path_to(target.name)[0]
        return farm(view)


def farm(view):
    """Walk to the field or dungeon with the most EXP per visit that the party can survive, then
    bounce in and out. (Places you have not visited yet count by their level.)"""
    spots = [p for p in view.known.values()
             if p.kind in ("field", "dungeon") and p.ok and (p.name == view.here or view.path_to(p.name))]
    if not spots:
        return view.neighbors[0]
    best = max(spots, key=lambda p: (p.exp is None or p.exp > 0, p.exp or 0, p.level))
    if best.name != view.here:
        return view.path_to(best.name)[0]
    # already there: step out to a safe neighbour, and come back tomorrow
    safe = [n for n in view.neighbors if view.known[n].ok]
    return max(safe, key=lambda n: view.known[n].level) if safe else view.neighbors[0]
