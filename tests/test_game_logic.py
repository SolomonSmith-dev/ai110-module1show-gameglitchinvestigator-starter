from logic_utils import check_guess, update_score, get_range_for_difficulty

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)  # FIX: check_guess returns a tuple (outcome, message)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)  # FIX: check_guess returns a tuple (outcome, message)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)  # FIX: check_guess returns a tuple (outcome, message)
    assert outcome == "Too Low"


# --- Tests targeting fixed bugs ---

def test_check_guess_int_comparison_works():
    # BUG FIX: secret was cast to str on even attempts, so 50 != "50".
    # Verify that check_guess correctly identifies a win with matching integers.
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    # Verify near misses still work correctly as integers
    outcome, message = check_guess(49, 50)
    assert outcome == "Too Low"
    outcome, message = check_guess(51, 50)
    assert outcome == "Too High"

def test_score_never_goes_negative():
    # BUG FIX: score could go negative from repeated wrong guesses.
    # Start at 0 and deduct — should stay at 0, not go to -5.
    score = update_score(0, "Too High", 1)
    assert score == 0
    score = update_score(0, "Too Low", 2)
    assert score == 0

def test_score_deducts_consistently_for_too_high():
    # BUG FIX: "Too High" was awarding +5 on even attempts instead of deducting.
    # Both even and odd attempts should deduct 5.
    score_odd = update_score(20, "Too High", 1)
    score_even = update_score(20, "Too High", 2)
    assert score_odd == 15
    assert score_even == 15  # Was incorrectly 25 before fix

def test_easy_range_is_1_to_20():
    # BUG FIX: range was hardcoded to 1-100. Verify Easy returns correct range.
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20
