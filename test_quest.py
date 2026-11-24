"""Checks that the game rules work and every test map can be won. Run: python test_quest.py"""
from quest import Quest
from run import TEST_MAPS


def winnable(q):
    """Can the final gate be reached at all? (any level can be farmed, so only items matter)"""
    items, done, reach = set(), set(), {q.start}
    while True:
        grew = False
        for name in list(reach):
            p = q.places[name]
            if set(p.needs) <= items and set(p.after) <= done and name not in done:
                done.add(name)
                items.update(p.gives)
                grew = True
            if name in done:
                for n in p.links:
                    if n not in reach:
                        reach.add(n)
                        grew = True
        if not grew:
            return q.final in done


def test_every_test_map_is_winnable():
    for name in TEST_MAPS:
        assert winnable(Quest.load(name)), name


def test_fog_of_war():
    v = Quest.load("ff1").view()
    assert v.here == "Cornelle Castle" and v.final is None
    assert set(v.known) == {"Cornelle Castle", *v.neighbors}
    assert v.known["Fiend Shrine"].gives is None           # unknown until you get it


def test_turned_away_wiped_and_rewarded():
    q = Quest.load("ff1")
    q.move("Pravok Port")                                  # needs the Bridge
    assert q.here == "Cornelle Castle" and q.day == 1 and "turns" in q.last
    q.move("Fiend Shrine")                                 # level 3 gate at LV 1
    assert q.here == "Cornelle Castle" and "level:3" in q.last
    q.level = 3
    q.move("Fiend Shrine")
    assert q.items == {"Lute", "Bridge"} and q.level > 3
    q.move("Cornelle Castle")
    q.level = 1
    q.move("Pravok Port")                                  # a level 4 dungeon at LV 1: wiped
    assert q.here == "Cornelle Castle" and q.day == 5 + 3 and "Wiped" in q.last
    assert q.view().known["Fiend Shrine"].gives == ("Lute", "Bridge")


def test_path_avoids_blocked_places():
    q = Quest.load("ff1")
    q.items, q.level = {"Bridge", "Ship"}, 4
    q.move("Pravok Port")
    q.move("Elfhaven")
    v = q.view()
    assert v.path_to("Pravok Port") == ["Pravok Port"]
    assert v.path_to("Northwest Keep", safe=True) == ["Northwest Keep"]   # a blocked target is fine
    assert v.path_to("Nowhere") is None


if __name__ == "__main__":
    tests = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"{len(tests)}/{len(tests)} passed")
