"""The autograder: checks your quiz (quiz.py) and your agent (my_policy.py).

    python grade.py

GitHub runs this same file every time you push to your fork (.github/workflows/grade.yml). When
every check passes you get a green check mark on GitHub: that is what you hand in (README, Step 8).
"""
import datetime
import hashlib
import importlib
import os
import re
import sys

from run import TEST_MAPS, run_one

MIN_WON = 25        # test maps your agent must win (out of 31), and the FF1 map must be one of them
# sha256 of "Q<n>:<letter>", cut to 12 characters, so the answers cannot be read here
ANSWERS = {"Q1": "4a5e67b48b7f", "Q2": "95c98c7698b2", "Q3": "bc7e8c22d6e7",
           "Q4": "604bb588be5c", "Q5": "a5491def54d2", "Q6": "378aa8fa08d8"}


def load(module):
    """(module, None), or (None, what went wrong in one line)"""
    try:
        return importlib.import_module(module), None
    except Exception as e:                                 # a typo in the student's file
        line = getattr(e, "lineno", None) or (e.__traceback__ and e.__traceback__.tb_next and
                                               e.__traceback__.tb_next.tb_lineno)
        return None, f"{module}.py line {line}: {type(e).__name__}: {e}"


def grade():
    """Returns (name, checks): checks is a list of (passed, text)."""
    checks = []
    quiz, err = load("quiz")
    if err:
        checks.append((False, f"quiz.py does not load: {err}"))
    name = str(getattr(quiz, "NAME", "")).strip()
    checks.append((bool(name), f"Name: {name}" if name else 'Name: write it in quiz.py, NAME = "..."'))
    for q, key in ANSWERS.items():
        a = str(getattr(quiz, q, "")).strip().lower()
        ok = hashlib.sha256(f"{q}:{a}".encode()).hexdigest()[:12] == key
        checks.append((ok, f"{q} correct" if ok else f"{q} not answered yet" if not a else f"{q}: '{a}' is not right, see the slide named in quiz.py"))

    agent, err = load("my_policy")
    if err or not hasattr(agent, "Policy"):
        checks.append((False, f"my_policy.py does not load: {err or 'class Policy is missing'}"))
        return name, checks
    results = [run_one(agent.Policy, m) for m in TEST_MAPS]
    crash = next((e for _, _, e in results if e), None)
    if crash:
        where = re.findall(r'my_policy\.py", line (\d+)', crash)
        checks.append((False, f"Your agent crashed (my_policy.py line {where[-1] if where else '?'}): {crash.strip().splitlines()[-1]}"))
    else:
        checks.append((True, "Your agent runs on all 31 maps without crashing"))
    ff1_won, ff1_days, _ = results[0]                      # TEST_MAPS[0] is the FF1 map
    checks.append((ff1_won, f"Wins the FF1 map: day {ff1_days} of 350" if ff1_won else "Wins the FF1 map: lost (fill in the two TODOs in my_policy.py)"))
    days = [d for won, d, _ in results if won]
    checks.append((len(days) >= MIN_WON, f"Wins at least {MIN_WON} of the 31 test maps: {len(days)} won"
                   + (f", {sum(days) / len(days):.1f} days on average" if days else "")))
    return name, checks


def report(name, checks):
    """Prints the result; on GitHub also writes it to the run's summary page. True when passed."""
    passed = all(ok for ok, _ in checks)
    n = sum(ok for ok, _ in checks)
    when = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    color = sys.stdout.isatty() or "GITHUB_ACTIONS" in os.environ
    paint = (lambda code, s: f"\033[{code}m{s}\033[0m") if color else (lambda code, s: s)
    print(paint("1", "\n  Quest Agent Challenge: autograder\n"))
    for ok, text in checks:
        print("  " + (paint("32", "✓") if ok else paint("31", "✗")) + "  " + text)
    verdict = paint("1;42;30", " PASSED ") if passed else paint("1;41;37", " NOT YET ")
    print(f"\n  {verdict}  {n}/{len(checks)} checks   {name or '(no name)'}   {when}")
    print("  " + ("Push to GitHub, open the Actions tab, and screenshot the green check for Canvas."
                  if passed else "Fix the ✗ lines above, then run python grade.py again.") + "\n")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## {'✅ PASSED' if passed else '❌ NOT YET'}: {name or '(no name in quiz.py)'}\n\n")
            f.write(f"{n} of {len(checks)} checks passed, graded {when}.\n\n| | Check |\n|---|---|\n")
            f.writelines(f"| {'✅' if ok else '❌'} | {text} |\n" for ok, text in checks)
    return passed


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):                 # ✓ and ✗ on any Windows terminal
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if os.name == "nt":
        os.system("")              # a fixed empty command: the known way to turn on colours in the Windows console
    sys.exit(0 if report(*grade()) else 1)
