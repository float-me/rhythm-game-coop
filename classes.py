from constants import *
from typing import Set, List, Dict
import math

class Rope: # Knot가 될 수도 있는 무언가
    def __init__(self, start: int, knot: Knot, length: int, rating: int, input_count: int):
        self.start, self.knot, self.length, self.rating = start, knot, length, rating
        self.n = self.knot.rhythm.n
        self.count = 1
        self.input_counts = [input_count]

    def __repr__(self) -> str:
        return f"""**
KNOT: {self.knot}
COUNT: {self.count}
START: {self.start}
RATING: {RATINGS[self.rating]}
LENGTH: {self.length}

"""
        
    def apply(self, input_count: int):
        self.count += 1
        self.input_counts.append(input_count)

    @property
    def interval(self):
        beats = sum(self.knot.rhythm.ratio[:self.count])
        midpoint = (self.start + beats * self.length)/ RHYTHM_GRID
        distance = self.length * RATING_RULE[self.rating] / RHYTHM_GRID
        return (midpoint - distance, midpoint + distance)
    
    def is_complete(self) -> bool:
        return self.n == self.count

class Map:
    def __init__(self) -> None:
        self.count = 1
        self.deck = [self.pick() for _ in range(3)]
        self.nexts = [self.pick() for _ in range(5)]
        self.deck_rating = [3, 3, 3]
        self.combo_rating = 0
        self.combo_count = 0
        self.timeline: List[Tuple[float, Rope, bool]] = []
        self.alive: List[Rope] = []
        self.open: List[Rope] = []
        self.input_count = 0
        self.combo_check: Dict[int, List[int]] = {}
    
    def pick(self):
        val = pick_random_at(self.count)
        self.count += 1
        return val
    
    def create_ropes(self, time_input: float, available_pattern: Set[Knot]):
        for rating in range(3):
            rating_rule = RATING_RULE[rating]
            for pattern in available_pattern:
                for length in pattern.rhythm.length_available:
                    distance = length / RHYTHM_GRID * rating_rule
                    low = math.ceil(RHYTHM_GRID * (time_input - distance))
                    high = math.trunc(RHYTHM_GRID * (time_input + distance))
                    for start in range(low, high + 1):
                        self.alive.append(
                            Rope(start, pattern, length, rating, self.input_count)
                        )
                        if self.input_count in self.combo_check:
                            self.combo_check[self.input_count][rating] += 1
                        else:
                            self.combo_check[self.input_count] = [0, 0, 0]
                            self.combo_check[self.input_count][rating] += 1

    def kill(self, rope: Rope):
        self.open.remove(rope)
        self.alive.remove(rope)
        self.minus_combo_check(rope)
    
    def minus_combo_check(self, rope: Rope):
        for count in rope.input_counts:
            if count in self.combo_check:
                self.combo_check[count][rope.rating] -= 1
                if self.combo_check[count][rope.rating] == 0:
                    if sum(self.combo_check[count][:self.combo_rating + 1]) == 0:
                        print(count)
                        self.combo_break()
                        return

    def combo_break(self):
        print("Ta-da! Combo Break!")

    def write_timeline(self, time_current: float):
        self.timeline = []
        for rope in self.alive:
            s, e = rope.interval
            if s > time_current:
                self.timeline.append((s, rope, True))
            if e > time_current:
                self.timeline.append((e, rope, False))
        self.timeline.sort(key=lambda x: x[0])

    def update(self, time_current: float):
        erase = 0
        for timing, rope, is_start in self.timeline:
            if timing < time_current:
                erase += 1
                if is_start:
                    self.open.append(rope)
                else:
                    self.kill(rope)
            else:
                break
        self.timeline = self.timeline[erase:]

    def get_accepted(self):
        done: List[Rope] = []
        for rope in self.open:
            rope.apply(self.input_count)
            if rope.is_complete():
                done.append(rope)
        done.sort(key=lambda x: (x.rating, x.knot.priority))
        accepted: List[Rope] = []
        accepted_idxs: List[int] = []
        deck = self.deck[:]
        for rope in done:
            self.kill(rope)
            if rope.knot in deck:
                idx = deck.index(rope.knot)
                deck[idx] = 0
                accepted.append(rope)
                accepted_idxs.append(idx)
        
        return accepted, accepted_idxs
    
    def control_accepted(self) -> bool:
        accepted, accepted_idxs = self.get_accepted()
        is_accepted_exist = (accepted != [])
        for i, rope in enumerate(accepted):
            idx = accepted_idxs[i]
            if rope.rating <= self.combo_rating:
                for input_count in rope.input_counts:
                    if input_count in self.combo_check:
                        del self.combo_check[input_count]
                self.deck[idx] = self.nexts[0]
                self.deck_rating[idx] = 3
                self.nexts = [*self.nexts[1:], self.pick()]
                self.combo_count += 1
            else:
                self.deck_rating[idx] = rope.rating
                for input_count in rope.input_counts:
                    if input_count in self.combo_check:
                        self.combo_check[input_count][rope.rating] = -1

        return is_accepted_exist
    
    def write_alive(self, time_input: float):
        alive = []
        for rope in self.alive:
            if rope.knot in self.deck:
                alive.append(rope)
            else:
                if rope in self.open:
                    self.open.remove(rope)
                    self.minus_combo_check(rope)
        self.alive = alive
        self.create_ropes(time_input, set(self.deck))

    def apply(self, time_input: float):
        self.input_count += 1
        
        is_accepted_exist = self.control_accepted()
        self.write_alive(time_input)
        self.write_timeline(time_input)
        self.open = []
        
        # print(f"alive: {self.alive}")
        print(f"open: {self.open}")
        if is_accepted_exist:
            print(self.deck)
            print(self.deck_rating)
        
        # print(self.timeline)

        print("---------------\n\n")