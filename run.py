"""Score a route policy, or watch it play.

  python run.py                                   score my_policy.Policy on every test map
  python run.py --policy baselines:KeyChaser      score another policy
  python run.py --map ff1 --show                  watch one map day by day
  python run.py --map seed:7 --show               watch a generated map
"""
import argparse
import importlib
import traceback

from quest import Quest, play

TEST_MAPS = ["ff1"] + [f"seed:{s}" for s in range(1, 31)]


def load_policy(spec):
    module, _, cls = spec.partition(":")
    return getattr(importlib.import_module(module), cls or "Policy")


def run_one(policy_cls, name, show=False):
    """(won, days used, error text or None)"""
    q = Quest.load(name)
    try:
        play(policy_cls(), q, show)
    except Exception:                                      # a bug in the policy loses this map only
        return False, q.days, traceback.format_exc()
    return q.won, q.day, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--policy", default="my_policy:Policy", help="module:Class (default my_policy:Policy)")
    ap.add_argument("--map", help="play one map: ff1, seed:<n> or a .json path")
    ap.add_argument("--show", action="store_true", help="print every day")
    a = ap.parse_args()
    policy_cls = load_policy(a.policy)
    maps = [a.map] if a.map else TEST_MAPS
    won, days, shown = 0, [], False
    for name in maps:
        ok, used, err = run_one(policy_cls, name, a.show)
        if err and not shown:
            print(err)
            shown = True
        won += ok
        days.append(used) if ok else None
        print(f"{name:<8} {'WON ' if ok else 'lost'} in {used:3} days" + ("  (policy crashed)" if err else ""))
    mean = sum(days) / len(days) if days else float("nan")
    print(f"\n{a.policy}: won {won}/{len(maps)} maps, mean {mean:.1f} days on the maps it won")


if __name__ == "__main__":
    main()
