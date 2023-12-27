from constants import *
from typing import Set, List, Dict, Self
import math
import pygame

def time_input_to_grid(time_input: float) -> List[List[int]]:
    grid_val = RHYTHM_GRID * (time_input % 1)
    res = []
    for rating in range(RATING_COUNTS):
        rule = RATING_RULE[rating]
        low = max(math.ceil(grid_val - rule), 1)
        high = min(math.floor(grid_val + rule), RHYTHM_GRID - 1)
        res.append(list(range(low, high + 1)))
    return res

def smallest_grid_from_time_input(time_input: float) -> int:
    grid_val = RHYTHM_GRID * (time_input % 1)
    rule = RATING_RULE[-1]
    return math.ceil(grid_val - rule) % RHYTHM_GRID

class Rope:
    def __init__(self, start: int, knot: Knot, length: int, rating: int, key_no: int, input_count: int) -> None:
        assert 0 < start < RHYTHM_GRID
        self.start, self.knot, self.length, self.rating = start, knot, length, rating
        self.count = 1
        self.key_nos = [key_no]
        self.input_counts = [input_count]
        self.n = self.knot.rhythm.n
        self.identity = self.knot.rhythm.identity
    
    @property
    def next(self):
        beats = sum(self.knot.rhythm.ratio[:self.count])
        return self.start + beats * self.length
    
    @property
    def last(self):
        return (self.input_counts[-1], self.key_nos[-1])

    def apply(self, key_no: int, input_count: int):
        self.count += 1
        self.key_nos.append(key_no)
        self.input_counts.append(input_count)
    
    def __repr__(self) -> str:
        return f"""{self.knot}
RATING: {RATINGS[self.rating]}
COUNTS: {self.input_counts}
KEYS: {self.key_nos}"""
    
    def collide_with(self, other: Self) -> bool:
        my_set = set(zip(self.input_counts, self.key_nos))
        other_set = set(zip(other.input_counts, other.key_nos))
        identity = min(self.identity, other.identity)
        return len(my_set & other_set) >= identity
    
    @property
    def available_keys(self) -> List[int]:
        all_keys = list(range(1, KEY_COUNTS + 1))
        match self.knot.key_type:
            case "free":
                return all_keys
            case "one":
                return [self.key_nos[-1]]
            case "slide":
                if self.count == 1:
                    my_keys = {self.key_nos[0] - 1, self.key_nos[0] + 1}
                else:
                    my_keys = {2 * self.key_nos[-1] - self.key_nos[-2]}
                return list(my_keys & set(all_keys))
            case "trill":
                if self.count == 1:
                    return [key for key in all_keys if key != self.key_nos[0]]
                else:
                    return [self.key_nos[-2]]
    
    def is_complete(self) -> bool:
        return self.n == self.count

class Map:
    def __init__(self) -> None:
        self.count = 1
        self.deck = [self.pick() for _ in range(DECK_SIZE)]
        self.nexts = [self.pick() for _ in range(NEXT_SIZE)]
        self.deck_rating = [RATING_COUNTS] * DECK_SIZE
        self.combo_rating = 0
        self.combo_count = 0
        self.bar = 0

        self.input_count = 0

        self.timeline: List[List[List[Rope]]] = [[[] for _ in range(RATING_COUNTS)] for _ in range(RHYTHM_GRID)]
        self.done: List[List[Rope]] = [[] for _ in range(RHYTHM_GRID)]
        self.accept: List[Rope|None] = [None] * DECK_SIZE

        self.finish: List[Rope] = []
        
        self.marks = []

    def pick(self):
        val = pick_random_at(self.count)
        self.count += 1
        return val
    
    def create_ropes(self, time_input: float, key_no: int, available_knot: Set[Knot]):
        in_grid = time_input_to_grid(time_input)
        for rating in range(RATING_COUNTS):
            for start in in_grid[rating]:
                for knot in available_knot:
                    for length in knot.rhythm.length_available:
                        end = start + length * knot.rhythm.identity
                        if end >= RHYTHM_GRID:
                            continue
                        rope = Rope(
                            start, knot, length, rating, key_no, self.input_count
                        )
                        self.timeline[rope.next][rating].append(rope)
    
    def on_bar_change(self):
        is_combo_left = True
        input_counts = set()
        while is_combo_left:
            for rope in self.finish:
                input_counts |= set(rope.input_counts)
            self.finish = []
            if len(input_counts) < self.input_count:
                is_combo_left = self.combo_break()
                continue
            break
        self.input_count = 0
        self.timeline = [[[] for _ in range(RATING_COUNTS)] for _ in range(RHYTHM_GRID)]
        self.accept = [None] * DECK_SIZE

    def combo_break(self) -> bool:
        self.combo_rating += 1
        
        if self.combo_rating == RATING_COUNTS:
            self.combo_count = 0
            self.combo_rating = 0
            return False

        self.write_finish()
        return True

    def update(self, time_current: float):
        bar = time_current // 1
        if bar > self.bar:
            self.bar = bar
            self.on_bar_change()
    
    def apply(self, grid: List[List[int]], key_no: int):
        this_input = (self.input_count, key_no)
        for rating in range(RATING_COUNTS):
            for new in grid[rating]:
                applied: List[Rope] = []
                for rope in self.timeline[new][rating]:
                    if key_no not in rope.available_keys:
                        continue
                    if rope.last == this_input:
                        continue
                    rope.apply(key_no, self.input_count)
                    applied.append(rope)
                for rope in applied:
                    self.timeline[new][rating].remove(rope)
                    if rope.is_complete():
                        self.done[rating].append(rope)
                    else:
                        self.timeline[rope.next][rating].append(rope)
            self.done[rating].sort(key=lambda x: x.knot.priority)

    def is_collided(self, rope: Rope) -> bool:
        for other in self.finish:
            if rope.collide_with(other):
                return True
        for other in self.accept:
            if other != None:
                if rope.collide_with(other):
                    return True
        return False

    def write_accept(self):
        deck = self.deck[:]
        for rating in range(RATING_COUNTS):
            for rope in self.done[rating]:
                if rope.knot in deck and not self.is_collided(rope):
                    idx = deck.index(rope.knot)
                    deck[idx] = 0
                    self.accept_rope(rope, idx)
        self.done = [[] for _ in range(RHYTHM_GRID)]
    
    def write_finish(self):
        for idx, rope in enumerate(self.accept):
            if rope != None and rope.rating <= self.combo_rating:
                self.finish_rope(rope, idx)
    
    def accept_rope(self, rope: Rope, idx: int):
        self.accept[idx] = rope
        self.deck_rating[idx] = rope.rating
    
    def finish_rope(self, rope: Rope, idx: int):
        self.finish.append(rope)
        self.accept[idx] = None
        self.deck[idx] = self.nexts[0]
        self.deck_rating[idx] = RATING_COUNTS
        self.nexts = [*self.nexts[1:], self.pick()]
        self.combo_count += 1
    
    def on_input_at(self, time_input: float, key_no: int):
        self.input_count += 1

        grid = time_input_to_grid(time_input)

        self.apply(grid, key_no) # open의 각 rope에 입력이 들어왔음을 알리고, .done을 작성
        
        self.write_accept() # .done을 바탕으로 .accept를 작성
        self.write_finish() # .accept를 바탕으로 .finish를 작성

        self.create_ropes(time_input, key_no, set(self.deck))

class PlayerMap(Map):
    def __init__(self) -> None:
        super().__init__()
        self.hp = 100
        self.hp_pre = 100
    
    def set_game(self, game: 'TwoPlayerGame', position: int):
        self.game = game
        self.opponent = game.players[1 - position]
    
    def on_bar_change(self):
        self.hp = self.hp_pre
        return super().on_bar_change()
    
    def damage_of(self, rope: Rope):
        DAMAGE_RATE[self.combo_rating] * min(self.combo_count, COMBO_BONUS_LIMIT)

    def finish_rope(self, rope: Rope, idx: int):
        self.attack()
        return super().finish_rope(rope, idx)
    
    def attack(self, damage):
        self.opponent.hp_pre -= damage

class TwoPlayerGame:
    def __init__(self, p1: PlayerMap, p2: PlayerMap) -> None:
        self.players = [p1, p2]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 5)
        self.velocity = random.uniform(3, 7) * 0.3
        self.angle = random.uniform(0, 2 * math.pi)
        self.acceleration = -0.05  # Deceleration rate
        self.alpha = 255
        self.life = 0.4

    def update(self):
        self.velocity += self.acceleration
        self.x += self.velocity * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle)
        self.alpha -= int(255 * (1 / (60 * self.life)))

    def draw(self, screen):
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2], self.alpha), (int(self.x), int(self.y)), self.radius)



class Mark:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []

    def update_particles(self):
        for particle in self.particles:
            particle.update()
            if particle.alpha <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        for particle in self.particles:
            particle.draw(screen)

    def create_particles(self):
        for _ in range(20):
            particle = Particle(self.x, self.y, self.color)
            self.particles.append(particle)
            
            
# ComboText class
class ComboText:
    def __init__(self, x, y, combo_text):
        self.x = x
        self.y = y
        self.combo_text = combo_text
        self.font = pygame.font.Font(None, 36)
        self.size = 25
        self.velocity = 2
        self.acceleration = -0.08
        self.timer = 30  # Frames before disappearing

    def update(self):
        self.size += self.velocity
        self.velocity += self.acceleration


        self.timer -= 1

    def draw(self, screen):
        font = pygame.font.Font(None, int(self.size))
        text_surface = font.render(self.combo_text, True, (72, 209, 204))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x, self.y)
        screen.blit(text_surface, text_rect)

class Img:
    imgs = {}
    def __init__(self):
        for i in ["sample", "sample2"]:
            self.imgs[i] = pygame.transform.scale_by(pygame.image.load("res/" + str(i) + ".png").convert(), 0.2)

class Drawing:
    def __init__(self, screen:pygame.Surface):
        self.screen = screen        

    def draw(self, drawing:str):
        '''|x_pos,y_pos,img_name|형식으로 이미지 처리'''
        for img in drawing.split("|"):
            x, y, name = img.split(",")
            self.screen.blit(Img.imgs[name], (int(x), int(y)))


class Animation:
    def __init__(self, frame:list[pygame.Surface], speed = 5):
        self.frame = frame
        self.speed = speed
        self.length = len(frame)
        self.tick = 0

    def play(self, display, x, y):
        display.blit(self.frame[self.tick//self.speed%self.length], (x, y))
        self.tick += 1
