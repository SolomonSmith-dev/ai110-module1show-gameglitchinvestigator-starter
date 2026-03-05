# Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it looked functional at a glance but had several hidden bugs that became apparent during gameplay. The UI loaded correctly with the difficulty selector and guess input, but the numbers and scoring were off as soon as I started interacting with it.

**Bug 1 - Off-by-one in attempts counter:** The attempts counter started at 1 instead of 0, so on a fresh game with Easy difficulty (8 attempts allowed), the display showed "Attempts left: 7" before any guess was made. I expected to see the full 8 attempts available. The fix was changing the initial value of `st.session_state.attempts` from `1` to `0`.

**Bug 2 - Score going negative with inconsistent penalty logic:** The `update_score` function had two problems. For "Too High" guesses, it inconsistently awarded +5 points on even-numbered attempts instead of always deducting points. Additionally, there was no floor on the score, so repeated wrong guesses drove it into negative numbers. I expected wrong guesses to always cost points and the score to never drop below zero.

**Bug 3 - Hardcoded range in the guess prompt:** The info message always said "Guess a number between 1 and 100" regardless of the selected difficulty. On Easy mode (range 1-20) or Normal mode (range 1-50), this was misleading. I expected the displayed range to match the actual difficulty setting.

**Bug 4 - `logic_utils.py` stubs not implemented:** The `logic_utils.py` file contained only `NotImplementedError` stubs, so the test suite (`test_game_logic.py`) failed entirely. The tests also compared `check_guess` output to a plain string, but the function returns a tuple of `(outcome, message)`.

---

## 2. How did you use AI as a teammate?

I used GitHub Copilot (inline chat and agent mode) and Claude throughout this project. Copilot was the primary tool for refactoring logic out of `app.py` and into `logic_utils.py`, and Claude helped me reason through why certain bugs were happening at the logic level.

**Correct suggestion:** When I asked Copilot to explain why the score was going negative, it correctly identified that `update_score` had no floor on the return value for wrong guesses. It suggested wrapping the return with `max(current_score - 5, 0)`. I verified this by writing `test_score_never_goes_negative`, which starts the score at 0, calls `update_score` with a wrong outcome, and asserts the result is still 0. The test passed after the fix.

**Incorrect/misleading suggestion:** When I first asked Copilot to fix the `update_score` bug, it suggested adding a check at the top of the function that set `current_score = max(current_score, 0)` before any logic ran. That approach was wrong because it would still allow the function to return a negative value -- it only clamped the input, not the output. I caught this by manually tracing through the logic with `current_score = 3` and `outcome = "Too High"`: the clamped input was still 3, then minus 5 returned -2. I had to override the suggestion and apply `max(..., 0)` on each return statement individually instead.

---

## 3. Debugging and testing your fixes

I treated a bug as fixed only when two things were both true: the relevant pytest test passed, and I manually verified the behavior in the running Streamlit app. If only one of those was true I kept digging, because a test can pass on clean inputs while the live app still breaks on edge cases.

The most useful test was `test_score_deducts_consistently_for_too_high`. Before the fix, calling `update_score(20, "Too High", 2)` (an even attempt number) returned 25 instead of 15 because the original code had a branch that awarded +5 on even attempts. Running that test with the original code failed with `AssertionError: assert 25 == 15`, which gave me the exact line to go fix. After moving the fix into place, the test passed and I confirmed in the live game that the score only went down on wrong guesses.

Copilot helped me write the test structure -- I described what the bug was and it scaffolded the `assert` statements -- but I had to correct the expected values because it initially used the buggy expected output as the target, which would have made the test pass against broken code.

---

## 4. What did you learn about Streamlit and state?

The secret kept changing because Streamlit reruns the entire script from top to bottom every time the user interacts with anything -- clicking a button, typing in a field, anything. In the original code, `st.session_state.secret = random.randint(low, high)` ran unconditionally, so it picked a new random number on every rerun. You could be one guess away from winning, click submit, and the secret would silently change underneath you.

The way I explain Streamlit reruns to someone new: think of the script like a web page that refreshes on every click. Every variable gets recreated from scratch unless you explicitly save it somewhere that survives the refresh. That storage is `st.session_state` -- it is a dictionary that persists between reruns for the current browser session. If you save a value there, it is still there after the next rerun.

The fix was wrapping the secret assignment in a guard: `if "secret" not in st.session_state`. That block only runs once -- the first time the page loads -- and every subsequent rerun skips it, leaving the secret untouched.

---

## 5. Looking ahead: your developer habits

The habit I want to carry forward is writing a failing test before I fix a bug. In this project I had a moment where I thought I fixed the score clamping issue, but I had not written the test yet. When I finally wrote it and ran it, it revealed my fix was incomplete. Writing the test first would have saved me that loop.

Next time I work with AI on a debugging task, I would not accept a suggested fix without tracing through the logic manually with at least one concrete example. Both times the AI gave me a wrong answer in this project, I could have caught it immediately by doing that. I trusted the output too quickly and had to backtrack.

This project changed how I think about AI-generated code: it can get the structure right and miss the logic entirely. The original game code looked plausible -- reasonable function names, reasonable structure -- but the actual comparisons and arithmetic were wrong in ways that only showed up when you ran it. AI is better at scaffolding than at correctness, and correctness is the part that actually matters.
