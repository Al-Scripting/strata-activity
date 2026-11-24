"""A learning agent: it scores every place it could head for with a weighted sum of features, and
walks toward the best one. The weights are not written by hand: train() finds them by playing
training maps, trying small random changes, and keeping the changes that do better (an
evolution strategy, one of the simplest ways to learn a policy).

    python learner.py                          train on seeds 100-111, save weights.json
    python learner.py --iters 200 --maps 20    train longer, on more maps
    python run.py --policy learner:LearnedPolicy

Ideas: add features, change the fitness, train on more maps, or replace the whole thing with
reinforcement learning (Q-learning over these features).
"""
import argparse
import json
import os
import random

from baselines import farm
from quest import Quest, play

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = os.path.join(HERE, "weights.json")
FEATURES = ["new place", "story place", "town", "fights", "level / party level", "steps away"]


def features(view, p, steps):
    """What the agent sees about one candidate place (a list of numbers, same order as FEATURES)."""
    return [float(not p.visited),
            float(p.kind in ("dungeon", "event", "gate") and not p.cleared),
            float(p.kind == "town"),
            float(p.kind in ("field", "dungeon")),
            p.level / max(1, view.level),
            steps / 10]


class LearnedPolicy:
    def __init__(self, weights=None):
        if weights is None:
            with open(WEIGHTS) as f:
                weights = json.load(f)
        self.w = weights

    def pick(self, view):
        best, best_score = None, float("-inf")
        for p in view.known.values():
            if p.name == view.here or not p.ok:
                continue
            path = view.path_to(p.name)
            if not path:
                continue
            score = sum(w * x for w, x in zip(self.w, features(view, p, len(path))))
            if score > best_score:
                best, best_score = path[0], score
        here = view.known[view.here]
        stay = sum(w * x for w, x in zip(self.w, features(view, here, 0)))
        if best is None or (here.kind in ("field", "dungeon") and stay > best_score):
            return farm(view)                     # fight here: step out and come back
        return best


def fitness(weights, seeds):
    """Maps won count most; fewer days break ties."""
    score = 0.0
    for s in seeds:
        q = play(LearnedPolicy(weights), Quest.load(f"seed:{s}"))
        score += 1000 if q.won else 0
        score -= q.day
    return score / len(seeds)


def train(iters=60, maps=12, sigma=0.5, seed=0):
    rng = random.Random(seed)
    seeds = list(range(100, 100 + maps))          # training maps; the test maps are seeds 1-30
    w = [rng.uniform(-1, 1) for _ in FEATURES]
    best = fitness(w, seeds)
    for i in range(iters):
        trial = [x + rng.gauss(0, sigma) for x in w]
        f = fitness(trial, seeds)
        if f > best:
            w, best = trial, f
            print(f"iter {i:3}: better, fitness {best:8.1f}  " + "  ".join(f"{n} {x:+.2f}" for n, x in zip(FEATURES, w)))
    return w, best


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--iters", type=int, default=60)
    ap.add_argument("--maps", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    w, f = train(a.iters, a.maps, seed=a.seed)
    with open(WEIGHTS, "w") as fh:
        json.dump(w, fh)
    print(f"saved {WEIGHTS}; now: python run.py --policy learner:LearnedPolicy")
