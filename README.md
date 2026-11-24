# Quest Agent Challenge

An agent has to take a party through a quest map. It has to find places, collect key items, get
strong enough for each boss, and beat the last one. You build the agent's decision: every day,
where does the party go next? Write rules, use search, or make it learn.

The game comes from STRATA, our project where learned agents play FINAL FANTASY. Here it is small
enough to play thousands of times a second, so you can try ideas fast.

It runs on plain Python 3.9 or newer, with nothing to install and no GPU.

## Start

1. Fork this repo on GitHub, then clone your fork.
2. Run the tests, the two baselines, and the learning agent:

```
python test_quest.py
python run.py --policy baselines:RandomWalk
python run.py --policy baselines:KeyChaser
python learner.py
python run.py --policy learner:LearnedPolicy
```

3. Write your own agent in `my_policy.py` and score it with `python run.py`.

## The game

The map is a graph of places. Every day you pick one neighbouring place and the party walks there.

| Place | What happens |
|---|---|
| town | Safe. After a wipe the party wakes up in the last town it visited. Some towns hand over a key item. |
| field | 10 random battles: EXP. |
| dungeon | 10 battles, plus a boss and key items the first time. |
| event | A person who trades: bring the key items they need and they give you new ones. |
| gate | A boss. It turns you away until you hold its key items and have its level. The final gate wins the map. |

- **Turned away:** a place you lack key items for (or a gate you are too weak for) costs a day, and you stay where you were.
- **Wiped:** entering a field or dungeon below its level sends you to the last town and costs 3 extra days.
- **Fog of war:** you only see places you have visited and their neighbours. You learn what a place gives only after you get it.
- **Levels and EXP:** FINAL FANTASY's level table, and a battle's EXP is shared by the 4 characters.

There are 31 test maps. `maps/ff1.json` is FINAL FANTASY's quest line: 42 places from the first
castle to the last boss, 350 days. The other 30 (`seed:1` to `seed:30`) are generated, with 4 to 6
regions and 150 days per region. Train on other seeds (100 and up) so that the test stays fair.

### Where the numbers come from

| Number | Source |
|---|---|
| Level table | FINAL FANTASY (NES), read from Disch's FF1 disassembly |
| EXP of each place | the mean EXP of one battle in that area of the NES game, times 10 battles, shared by 4 |
| Boss EXP | the boss's EXP in the NES game, shared by 4 |
| Boss and dungeon levels | the recommended levels in RPGSite's FF1 boss guide (A. Donaldson, 2021) |
| Field levels | our choice: the level of the boss that opens the field's region |
| Generated maps | a battle at level L pays `6 x L²`, a fit to FF1's areas |

## Your agent

```python
class Policy:
    def __init__(self):          # a new Policy for every map: keep memory in self
        pass

    def pick(self, view):        # return one of view.neighbors
        ...
```

`view` holds everything the party knows. The full list is at the top of `my_policy.py`; the most
useful parts are below.

- `view.known[name]`: a `PlaceInfo` for each place you have seen. `.ok` is `True` when you can enter it safely, and `.blocked_by` says why not (`["item:Crown", "level:10"]`).
- `view.path_to(name)`: the shortest known path that only walks through places you can enter, or `None` if there is none.
- `view.final`: the last boss's name once you have seen it.

Watch any agent play one map, day by day:

```
python run.py --map ff1 --show
python run.py --map seed:7 --show --policy baselines:KeyChaser
```

## The learning agent

`learner.py` does not have a hand-written rule. For every place it could head for, it computes six
features (is it new, is it a story place, a town, does it have fights, how strong is it compared
with the party, how many steps away) and scores the place with a weighted sum. It walks toward the
best score.

The six weights are learned. `python learner.py` plays training maps (seeds 100 to 111), tries a
small random change to the weights, and keeps the change if the agent does better. This is an
evolution strategy, one of the simplest ways to learn a policy. About 12 seconds of training
reached 29 of 31 test maps.

## Tasks

1. **Why does KeyChaser get stuck?** Run it on `ff1` with `--show`. Find the day it stops making
   progress and write two sentences on why at the top of `my_policy.py`. Hint: what does it never do?
2. **Win the FF1 map** within 350 days.
3. **Win all 31 test maps.** A rule tuned to one map can fail on the others.
4. **Use fewer days.** Our 10-line explorer wins all 31 with a mean of about 285 days. The learned
   agent above used about 274 on the maps it won. Beat both.
5. **Make the learner better.** Add features, train longer or on more maps, or change what it is
   rewarded for. Stretch: replace the evolution strategy with reinforcement learning (Q-learning
   over the same features).
6. **Stretch:** write a map in `maps/` that beats a classmate's agent. It must still pass
   `winnable()` in `test_quest.py`.

When you are done, push to your fork and share the last line of `python run.py` with the link.

## Background

In STRATA, a route network makes this same decision in the real FINAL FANTASY: given what the party
has found so far, which place next. It is a neural network trained with reinforcement learning
(PPO), first on generated maps like these and then in the game itself.

The place and item names follow FINAL FANTASY's, in STRATA's own spelling. FINAL FANTASY is a
trademark of Square Enix. This repo holds no game code or art; its numbers are facts read from a
public disassembly of the NES game and a public guide.
