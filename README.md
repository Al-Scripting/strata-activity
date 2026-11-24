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
| field | 10 random battles: EXP. |
| dungeon | 10 battles, plus a boss and key items the first time. |
| event | A person who trades: bring the key items they need and they give you new ones. |
| gate | A boss. It turns you away until you hold its key items and have its level. The final gate wins the map. |

- **Turned away:** a place you lack key items for (or a gate you are too weak for) costs a day, and you stay where you were.
- **Wiped:** entering a field or dungeon below its level sends you to the last town and costs 3 extra days.
- **Fog of war:** you only see places you have visited and their neighbours. You learn what a place gives only after you get it.
- **Levels and EXP are FINAL FANTASY's:** the NES level table (40 EXP for level 2, 11,116 for level 10, 96,332 for level 20), and a battle's EXP is shared by the 4 characters.

`maps/ff1.json` is the FINAL FANTASY quest line from STRATA's `ff1_main` spec: 42 places from
Cornelle Castle to Chaos, 350 days. The other 30 test maps are generated (`seed:1` to `seed:30`)
with 4 to 6 regions and 150 days per region.

### Where the numbers come from

| Number | Source |
|---|---|
| Level table | FINAL FANTASY (NES), read from Disch's FF1 disassembly |
| EXP of each place | the mean EXP of one battle in that area of the NES game (its encounter tables and monsters, same disassembly), times 10 battles, shared by 4 |
| Boss EXP | the boss's EXP in the NES game, shared by 4 |
| Boss and dungeon levels | the recommended levels in RPGSite's FF1 boss guide (A. Donaldson, 2021): Garland 3, Marsh Cave 10, Astos 10, Vampire 12, Lich 16, Marilith 20, Evil Eye 21, Citadel 23, Kraken 25, Tiamat 34, Chaos 35 |
| Field levels | our choice: the level of the boss that opens the field's region |
| Generated maps | a battle at level L pays `6 x L²`, a fit to FF1's areas |

Some real-game details carry over: the Power Peninsula pays about 7,000 EXP a visit at level 10,
the famous place to grind in FF1, and Chaos pays nothing.

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
2. **Win the FF1 map** within 350 days.
3. **Win all 31 test maps.** A rule tuned to FF1 can fail on generated maps.
4. **Use fewer days.** Our own 10-line explorer wins all 31 with a mean of about 285 days (235 on
   the FF1 map). Beat it.
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

## Compare: STRATA's agent in the real game

The party level when each boss fell, for STRATA's agent in the real game (run of 20 to 23 November
2026), RPGSite's recommended level, and our 10-line explorer on `maps/ff1.json`:

| Step | Agent in the real game | Recommended | Explorer here |
|---|---|---|---|
| Garland | 4 | 2-3 | 3 |
| Pirates | 6 | 3 | 4 |
| Marsh Cave | 20 | 10 | 10 |
| Astos | 20 | 10 | 10 |
| Vampire (Earth Cavern) | 28 | 12 | 12 |
| Lich | 36 | 16 | 16 |
| Marilith | 38 | 20 | 20 |
| Evil Eye (Ice Cavern) | 59 | 21 | 21 |
| Trial Citadel | 61 | 23 | 23 |

The real agent was about twice the recommended level. It kept fighting while our executor code was
stuck: between Marilith and the Ice Cavern it spent 29 hours and gained 21 levels while we fixed
the executor's Ice Cavern bugs. Can your policy reach Chaos near the recommended
levels, or does it grind like the agent?

The place and item names follow FINAL FANTASY's, in STRATA's own spelling. FINAL FANTASY is a
trademark of Square Enix. This repo holds no game code or art; its numbers are facts read from a
public disassembly of the NES game and a public guide.
