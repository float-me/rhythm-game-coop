import pygame
import time
from constants import *
from classes import Rope, Map

# Initialize Pygame
pygame.init()

# Set up display (not necessary for playing music, but Pygame initialization is required)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Music Player")

# Initialize mixer
pygame.mixer.init()

# Load music file
music_file = "tracks/DEAF KEV - Invincible [NCS Release].mp3"
pygame.mixer.music.load(music_file)
bpm = 100

TIMER_EVENT = pygame.USEREVENT + 1

beat_interval = 60 / bpm

# Play the music
pygame.mixer.music.play()

clock = pygame.time.Clock()
fps = 60

latency = 0 # 레이턴시, ms 단위

time_initial = time.time() + latency / 1000

map_p1 = Map()
print(map_p1.deck)

KEY_TIMING = [i / 4 for i in range(200)]
key_count = 0

# Main loop (to keep the program running while the music plays)
while True:
    time_current = (time.time() - time_initial)/beat_interval
    if time_current >= KEY_TIMING[key_count]:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN))
        key_count += 1
    map_p1.update(time_current)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            print(time_current)
            map_p1.apply(time_current)

     # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(fps)