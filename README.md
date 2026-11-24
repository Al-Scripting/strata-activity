# STRATA Route Challenge

In the talk you saw STRATA's agents play FINAL FANTASY (Pixel Remaster). Two networks make the
decisions: the **fight network** picks every battle command, and the **route network** picks where
the party goes next. This repo is the route problem in miniature. You write the rule that picks the
next place, and the score tells you how quickly it gets through the quest line.

It runs on plain Python 3.9 or newer. There is nothing to install, no game copy and no GPU, and a full
score takes about a second.

## Start

1. Fork this repo on GitHub, then clone your fork.
2. Run the tests and the two baselines:

```
python test_quest.py
python run.py --policy baselines:RandomWalk
python run.py --policy baselines:KeyChaser
```

3. Write your policy in `my_policy.py`, then score it with `python run.py`.

## The game

The map is a graph of places. Every day you pick one neighbouring place and the party walks there.

| Place | What happens |
|---|---|
| town | Safe. After a wipe the party wakes up in the last town it visited. Some towns hand over a key item. |
| field | Battles: `8 x level²` EXP per visit. |
| dungeon | Battles worth twice a field. The first clear hands over its key items. |
| event | A person who trades: bring the key items they need and they give you new ones. |
| gate | A boss. It turns you away until you hold its key items and have its level. Beating it pays 3x EXP. The final gate wins the map. |

- **Turned away:** a place you lack key items for (or a gate you are too weak for) costs a day, and you stay where you were.
- **Wiped:** entering a field or dungeon below its level sends you to the last town and costs 3 extra days.
- **Fog of war:** you only see places you have visited and their neighbours. You learn what a place gives only after you get it.
- **Levels:** going from level L to L+1 takes `10 x L²` EXP.

`maps/ff1.json` is the FINAL FANTASY quest line from STRATA's `ff1_main` spec: 42 places from
Cornelle Castle to Chaos, 250 days. The other 30 test maps are generated (`seed:1` to `seed:30`)
with 4 to 6 regions and 70 days per region.

## Your policy

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

Watch any policy play one map, day by day:

```
python run.py --map ff1 --show
python run.py --map seed:7 --show --policy baselines:KeyChaser
```

## Tasks

1. **Why does KeyChaser get stuck?** Run it on `ff1` with `--show`. Find the day it stops making
   progress and write two sentences on why at the top of `my_policy.py`. Hint: what does it never
   do? STRATA's real agent got stuck in a similar way, after 19 story steps.
2. **Win the FF1 map** within 250 days.
3. **Win all 31 test maps.** A rule tuned to FF1 can fail on generated maps.
4. **Use fewer days.** Our own 10-line explorer wins all 31 with a mean of about 135 days. Beat it.
   Ideas: farm only when a gate needs it, farm where the EXP per day is highest, and don't walk
   back to a town between battles.
5. **Stretch:**
   - Make your policy learn. Play generated maps with seeds 100 and up, keep what worked, then test on 1 to 30. Even a table of "which kind of place paid off" counts.
   - Write a map in `maps/` that beats a classmate's policy. It must still pass `winnable()` in `test_quest.py`.

When you are done, push to your fork and share the last line of `python run.py` with the link.

## How this maps to STRATA

| Here | STRATA in the real game |
|---|---|
| `pick(view)` | the route network (a PPO policy) picks the next quest node |
| `move()` | the executor walks, talks, shops and fights to get there |
| fog of war | the agent only knows places it has seen |
| a place that wants an item and gives nothing | Dragon King's Peak, which held the agent's objective for 2 hours |
| a town you must visit to see the next boss | Onrak, which the route network had learned to avoid |

The place and item names follow FINAL FANTASY's, in STRATA's own spelling. FINAL FANTASY is a
trademark of Square Enix. This repo holds no game code, art or data from the game.
