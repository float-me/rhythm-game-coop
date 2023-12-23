import random
from typing import List, Tuple

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

RHYTHM_GRID = 24

class Rhythm:
    def __init__(self, ratio: Tuple[int], length_available: List[int]) -> None:
        self.ratio = ratio
        self.length_available = length_available
        self.n = len(ratio) + 1

class Knot: # Mixture of Note and Knock, also a word
    def __init__(self, rhythm: Rhythm, key_type: str, priority: int, name: str) -> None:
        self.rhythm = rhythm
        self.key_type = key_type
        self.priority = priority
        self.name = name
    def __repr__(self) -> str:
        return f"KNOT {self.name}"

RHYTHM_TRIPLET = Rhythm((1, 1), [1, 2, 4, 8])
RHYTHM_QUAD = Rhythm((1, 1, 1), list(range(1, 7)))
RHYTHM_OFF2 = Rhythm((2, 1), list(range(1, 7)))
RHYTHM_OFF3 = Rhythm((1, 2), list(range(1, 7)))

KNOT_ONE3 = Knot(RHYTHM_TRIPLET, "one", 1, "one3")
KNOT_SLIDE4 = Knot(RHYTHM_QUAD, "slide", 2, "slide4")
KNOT_TRILL4 = Knot(RHYTHM_QUAD, "trill", 3, "trill4")
KNOT_FREE3 = Knot(RHYTHM_TRIPLET, "free", 4, "free3")
KNOT_FREE4 = Knot(RHYTHM_QUAD, "free", 5, "free4")
KNOT_TRILLOFF2 = Knot(RHYTHM_OFF2, "trill", 6, "trilloff2")
KNOT_TRILLOFF3 = Knot(RHYTHM_OFF3, "trill", 7, "trilloff3")

KNOTS = [KNOT_FREE3, KNOT_ONE3, KNOT_FREE4, KNOT_TRILL4, KNOT_TRILLOFF2, KNOT_TRILLOFF3]

RATINGS = ["Perfect", "Good", "Okay"]
RATING_RULE = [1/8, 1/6, 1/4]

def random_pattern_picker():
    while True:
        patterns = KNOTS[:]
        random.shuffle(patterns)
        for pattern in patterns:
            yield pattern

RANDOM_PATTERN_PICKER = random_pattern_picker()

def pick_random_at(n, info={}):
    if n in info:
        return info[n]
    info[n] = next(RANDOM_PATTERN_PICKER)
    return info[n]