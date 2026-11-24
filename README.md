# Quest Agent Challenge

An agent has to take a party through a quest map. It has to find places, collect key items, get
strong enough for each boss, and beat the last one. You build the agent's decision: every day,
where does the party go next? Write rules, use search, or make it learn.

The game comes from STRATA, our project where learned agents play FINAL FANTASY. Here it is small
enough to play thousands of times a second, so you can try ideas fast.

**Time:** about 1 hour for tasks 1 to 3, more if you go for the stretch goals.
**You need:** Python 3.9 or newer, git, and a GitHub account. Nothing to install with pip, no GPU.

## Step by step

### Step 0. Check Python

Open a terminal (Windows: PowerShell; macOS/Linux: Terminal) and run:

```
python --version
```

If it says `Python 3.9` or higher, you are set. On macOS and Linux the command may be `python3`
instead: use `python3` everywhere below. No Python? Install it from https://www.python.org/downloads/
(on Windows, tick "Add python.exe to PATH" in the installer).

### Step 1. Fork and clone

1. Open https://github.com/Al-Scripting/strata-activity and press **Fork** (top right). This makes
   your own copy under your account.
2. On your fork, press **Code**, copy the HTTPS address, and clone it:

```
git clone https://github.com/<your-username>/strata-activity.git
cd strata-activity
```

No git? Press **Code → Download ZIP** instead and unzip it. You can upload your files to your fork
on the GitHub website at the end.

Run every command below from inside the `strata-activity` folder.

### Step 2. Check that it runs

```
python test_quest.py
```

You should see six `PASS` lines and `6/6 passed`.

### Step 3. Watch an agent play

```
python run.py --policy baselines:KeyChaser --map ff1 --show
```

Each line is one day:

```
day   1  LV  2  Cornelle Fields        Reached Cornelle Fields. Battles: +60 EXP each.
day   2  LV  2  Cornelle Castle        Reached Cornelle Castle.
```

That is the day, the party's level, where the party is, and what happened. Scroll through it.
Find the last day something new happened (a `Got:` line), and look at what the agent does after
that. This is **task 1**: write two sentences on why it gets stuck at the top of `my_policy.py`.

### Step 4. Look at what your agent can see

Open Python with the FF1 map loaded:

```
python -i -c "from quest import Quest; q = Quest.load('ff1'); v = q.view()"
```

Then try:

```
>>> v.neighbors
['Cornelle Fields', 'Fiend Shrine', 'Pravok Port', 'Cornelle Vault']
>>> v.known['Fiend Shrine']
<gate 'Fiend Shrine' LV3 seen blocked_by=['level:3']>
>>> v.path_to('Pravok Port')
['Pravok Port']
>>> q.move('Cornelle Fields'); v = q.view(); v.level
'Reached Cornelle Fields. Battles: +60 EXP each.'
2
```

The Fiend Shrine is a boss that needs level 3. Pravok Port is next door, but it needs the Bridge,
so walking there now would only get you turned away. One trip to the fields took the party to
level 2. Type `exit()` to leave.

### Step 5. Write your agent

Open `my_policy.py`. It has a starter with four steps written as comments:

1. List the places worth going to: ones you can enter (`p.ok`) that are new, or story places
   (dungeon, event, gate) you have not cleared.
2. Keep the ones you can walk to (`view.path_to(p.name)` is not `None`).
3. Go to the nearest: `return view.path_to(best.name)[0]`.
4. If there is nothing worth visiting, you are too weak for the next boss: `return farm(view)`.

Fill in the two `TODO`s. Watch it with:

```
python run.py --map ff1 --show
```

### Step 6. Score it

```
python run.py
```

It plays all 31 test maps. Each line says whether a map was won and in how many days; the last
line is your score:

```
my_policy:Policy: won 30/31 maps, mean 283.9 days on the maps it won
```

(That is what the finished starter scores. One map is still lost: task 3.) More maps won is better; with the same number of maps, fewer days is better. If your agent
crashes, the error and the line it happened on are printed above the results.

### Step 7. Try the learning agent

```
python learner.py
python run.py --policy learner:LearnedPolicy
```

The first command trains for about 12 seconds and saves `weights.json`; the second scores it.
Read "The learning agent" below, then try `python learner.py --iters 200 --maps 20`.

### Step 8. Hand it in

```
git add my_policy.py learner.py
git commit -m "My quest agent"
git push
```

Share the link to your fork and the last line of `python run.py`.

## Tasks

| Task | Goal | Hint |
|---|---|---|
| 1. Why does KeyChaser get stuck? | two sentences in `my_policy.py` | What does it never do? |
| 2. Win the FF1 map | within 350 days | The starter in `my_policy.py` gets you most of the way |
| 3. Win all 31 test maps | 31 / 31 | A rule tuned to one map can fail on the others |
| 4. Use fewer days | beat about 285 days on average | Farm only when a boss needs it; farm where the EXP per day is highest |
| 5. Improve the learner | beat your own rules | New features, longer training, or reinforcement learning |
| 6. Stretch | a map that beats a classmate's agent | It must still pass `winnable()` in `test_quest.py` |

For reference, our own 10-line explorer wins all 31 with a mean of about 285 days, and the learning
agent after 12 seconds of training wins 29 with about 274.

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
Watch any map with `python run.py --map seed:7 --show`.

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
- `farm(view)` in `baselines.py`: walks to the strongest place you can survive and fights there.

## The learning agent

`learner.py` does not have a hand-written rule. For every place it could head for, it computes six
features (is it new, is it a story place, a town, does it have fights, how strong is it compared
with the party, how many steps away) and scores the place with a weighted sum. It walks toward the
best score.

The six weights are learned. `python learner.py` plays training maps (seeds 100 to 111), tries a
small random change to the weights, and keeps the change if the agent does better. This is an
evolution strategy, one of the simplest ways to learn a policy. Ways to improve it:

- Add a feature to `features()` and its name to `FEATURES` (for example: does the place have a level the party can survive?).
- Train longer or on more maps: `--iters 200 --maps 20`.
- Change `fitness()`: what should count as better?
- Stretch: replace the evolution strategy with Q-learning, using the same features as the state.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not found | Try `python3`, or `py` on Windows. Reinstall Python with "Add to PATH" ticked. |
| `ModuleNotFoundError: No module named 'quest'` | Run the commands from inside the `strata-activity` folder. |
| `'X' is not a neighbour of 'Y'` | `pick` must return one of `view.neighbors`; use `view.path_to(target)[0]`. |
| `learner:LearnedPolicy` fails with `weights.json` missing | Run `python learner.py` first. |
| Every map says `lost` | Watch one map with `--show` and look for where the agent stops making progress. |

## Background

In STRATA, a route network makes this same decision in the real FINAL FANTASY: given what the party
has found so far, which place next. It is a neural network trained with reinforcement learning
(PPO), first on generated maps like these and then in the game itself.

The place and item names follow FINAL FANTASY's, in STRATA's own spelling. FINAL FANTASY is a
trademark of Square Enix. This repo holds no game code or art; its numbers are facts read from a
public disassembly of the NES game and a public guide.
