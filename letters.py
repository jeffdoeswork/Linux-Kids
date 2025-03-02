import pygame
from pygame.locals import *
import random
import string
import math

# Initialize Pygame and set up the window (with extra padding)
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Keyboard Learning Game for Kids")

# Define Colors
BLACK = (0, 0, 0)
DULL_GRAY = (100, 100, 100)
BRIGHT_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAYISH_RED = (150, 50, 50)

# Set Up Fonts (increased sizes)
key_font = pygame.font.Font(None, 64)      # For key characters and buttons
message_font = pygame.font.Font(None, 80)   # For final message
timer_font = pygame.font.Font(None, 40)     # For timer display

# Keyboard layout parameters (bigger keys and spacing)
KEY_WIDTH = 90
KEY_HEIGHT = 90
KEY_SPACING = 30
KEYBOARD_TOP = 250  # Increased top margin for keyboard

# Define Keyboard Rows (including number row, though game letters are A-Z)
rows = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],  # First row: numbers
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],  # Second row: Q to P
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],        # Third row: A to L
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']                    # Fourth row: Z to M
]

# List of All 26 Letters for the Game (only uppercase letters)
letters = list(string.ascii_uppercase)

# Map Letters to Pygame Key Constants and Vice Versa
letter_to_key = {chr(ord('A') + i): globals()['K_' + chr(ord('a') + i)] for i in range(26)}
key_to_letter = {globals()['K_' + chr(ord('a') + i)]: chr(ord('A') + i) for i in range(26)}

# Game State Variables
game_state = 'not_started'
current_letter_index = 0
start_time = 0
final_time = 0
wrong_presses = {}

# Button Rectangles
start_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50, 200, 60)
quit_button = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 60)
# play_again_button will be defined in draw_play_again_button

# List to hold firework animations
fireworks = []  # each entry: {"center": (x,y), "start_time": ms}

# List to hold each coin's initial random rotation offset (for spinning coins)
coin_offsets = []

# ----------------------
# Drawing Functions
# ----------------------

# Draw a single key with background and text
def draw_key(surface, x, y, character, bg_color, text_color):
    key_rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)
    pygame.draw.rect(surface, bg_color, key_rect, border_radius=8)
    text = key_font.render(character, True, text_color)
    text_rect = text.get_rect(center=key_rect.center)
    surface.blit(text, text_rect)

# Get the center position of a given key letter (if present in rows)
def get_key_center(letter):
    for row_idx, row in enumerate(rows):
        if letter in row:
            row_width = len(row) * KEY_WIDTH + (len(row) - 1) * KEY_SPACING
            start_x = (SCREEN_WIDTH - row_width) / 2
            y = KEYBOARD_TOP + row_idx * (KEY_HEIGHT + KEY_SPACING)
            col_idx = row.index(letter)
            return (start_x + col_idx * (KEY_WIDTH + KEY_SPACING) + KEY_WIDTH / 2,
                    y + KEY_HEIGHT / 2)
    return (0, 0)

# Draw the entire keyboard with highlight and wrong press effects
def draw_keyboard(surface, highlighted_letter, wrong_presses, current_time):
    for row_idx, row in enumerate(rows):
        row_width = len(row) * KEY_WIDTH + (len(row) - 1) * KEY_SPACING
        start_x = (SCREEN_WIDTH - row_width) / 2
        y = KEYBOARD_TOP + row_idx * (KEY_HEIGHT + KEY_SPACING)
        for i, char in enumerate(row):
            x = start_x + i * (KEY_WIDTH + KEY_SPACING)
            if char == highlighted_letter:
                bg_color = BRIGHT_YELLOW
                text_color = BLACK
            elif char in wrong_presses:
                end_time = wrong_presses[char]
                remaining = max(0, (end_time - current_time) / 1000.0)
                if remaining > 0:
                    factor = remaining / 2.0
                    r = 100 + 50 * factor
                    g = 100 - 50 * factor
                    b = 100 - 50 * factor
                    bg_color = (int(r), int(g), int(b))
                    text_color = WHITE
                else:
                    bg_color = DULL_GRAY
                    text_color = WHITE
            else:
                bg_color = DULL_GRAY
                text_color = WHITE
            draw_key(surface, x, y, char, bg_color, text_color)

# Draw the start button
def draw_start_button(surface):
    pygame.draw.rect(surface, GREEN, start_button, border_radius=8)
    text = key_font.render("Start", True, BLACK)
    text_rect = text.get_rect(center=start_button.center)
    surface.blit(text, text_rect)

# Draw the "Quit Game" button (always visible)
def draw_quit_button(surface):
    pygame.draw.rect(surface, GRAYISH_RED, quit_button, border_radius=8)
    text = key_font.render("Quit", True, WHITE)
    text_rect = text.get_rect(center=quit_button.center)
    surface.blit(text, text_rect)

# Draw the "Play Again?" button on game finish (bigger and positioned higher)
def draw_play_again_button(surface):
    play_again_button = pygame.Rect((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT - 220, 300, 80)
    pygame.draw.rect(surface, GREEN, play_again_button, border_radius=8)
    text = key_font.render("Play Again?", True, BLACK)
    text_rect = text.get_rect(center=play_again_button.center)
    surface.blit(text, text_rect)
    return play_again_button

# Draw the timer
def draw_timer(surface, elapsed):
    text = timer_font.render(f"Time: {elapsed:.2f} s", True, WHITE)
    surface.blit(text, (20, 20))

# Draw the final message with a background box
def draw_final_message(surface, time_taken):
    text = message_font.render(f"Well Done! Time: {time_taken:.2f} sec", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 120))
    box_rect = text_rect.inflate(40, 30)
    pygame.draw.rect(surface, (50, 50, 50), box_rect)
    surface.blit(text, text_rect)

# Draw a spinning coin with a 3D effect by cycling through 5 shapes.
# The coin is rotated by 90° (using a phase shift) so that the oval and line are vertical.
def draw_spinning_coin(surface, center, coin_radius, phase):
    # Cycle through 5 phases:
    # [0.0, 0.2): Full circle (face of the coin)
    # [0.2, 0.4): Vertical oval
    # [0.4, 0.6): Bold vertical line (edge)
    # [0.6, 0.8): Vertical oval
    # [0.8, 1.0): Full circle
    if phase < 0.2 or phase >= 0.8:
        pygame.draw.circle(surface, BRIGHT_YELLOW, center, coin_radius)
        pygame.draw.circle(surface, WHITE, center, coin_radius, 2)
    elif phase < 0.4:
        rect = pygame.Rect(0, 0, int(coin_radius * 2 * 0.6), coin_radius * 2)
        rect.center = center
        pygame.draw.ellipse(surface, BRIGHT_YELLOW, rect)
        pygame.draw.ellipse(surface, WHITE, rect, 2)
    elif phase < 0.6:
        line_width = max(4, coin_radius // 2)
        rect = pygame.Rect(0, 0, line_width, coin_radius * 2)
        rect.center = center
        pygame.draw.rect(surface, BRIGHT_YELLOW, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
    else:
        rect = pygame.Rect(0, 0, int(coin_radius * 2 * 0.6), coin_radius * 2)
        rect.center = center
        pygame.draw.ellipse(surface, BRIGHT_YELLOW, rect)
        pygame.draw.ellipse(surface, WHITE, rect, 2)

# Draw coins at the bottom center (using the new 3D spinning effect)
def draw_coins(surface, num_coins, current_time):
    coin_radius = 20  # Bigger coins
    spacing = 10
    if num_coins > 0:
        total_width = num_coins * (2 * coin_radius) + (num_coins - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) / 2
        y = SCREEN_HEIGHT - (2 * coin_radius) - 40  # Extra margin from bottom for padding
        rotation_speed = 0.00314  # Faster spin (radians per millisecond)
        for i in range(num_coins):
            coin_center = (int(start_x + coin_radius + i * (2 * coin_radius + spacing)), int(y + coin_radius))
            # Calculate the coin's rotation angle and apply a 90° (pi/2) phase shift
            coin_angle = coin_offsets[i] + current_time * rotation_speed
            phase = ((coin_angle + math.pi/2) % (2 * math.pi)) / (2 * math.pi)
            draw_spinning_coin(surface, coin_center, coin_radius, phase)

# Draw firework animation on a key press (unchanged)
def draw_fireworks(surface, current_time):
    duration = 1500  # 1.5 seconds duration
    max_offset = 120
    finished = []
    for fw in fireworks:
        elapsed = current_time - fw["start_time"]
        if elapsed > duration:
            finished.append(fw)
            continue
        progress = elapsed / duration
        offset = progress * max_offset
        fade = max(0, 1 - progress)
        color = (int(BRIGHT_YELLOW[0] * fade),
                 int(BRIGHT_YELLOW[1] * fade),
                 int(BRIGHT_YELLOW[2] * fade))
        center_x, center_y = fw["center"]
        for angle_deg in range(0, 360, 45):
            angle_rad = math.radians(angle_deg)
            burst_x = center_x + offset * math.cos(angle_rad)
            burst_y = center_y + offset * math.sin(angle_rad)
            burst_radius = max(5 * (1 - progress), 2)
            pygame.draw.circle(surface, color, (int(burst_x), int(burst_y)), int(burst_radius))
        pygame.draw.circle(surface, color, (int(center_x), int(center_y)), int(5 * (1 - progress)))
    for fw in finished:
        fireworks.remove(fw)

# ----------------------
# Main Game Loop
# ----------------------
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if quit_button.collidepoint(event.pos):
                running = False
            if game_state == 'not_started' and start_button.collidepoint(event.pos):
                random.shuffle(letters)
                current_letter_index = 0
                start_time = pygame.time.get_ticks()
                game_state = 'in_progress'
                wrong_presses = {}
                coin_offsets = [random.uniform(0, 2 * math.pi) for _ in range(26)]
            if game_state == 'finished':
                play_again_button = pygame.Rect((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT - 220, 300, 80)
                if play_again_button.collidepoint(event.pos):
                    game_state = 'not_started'
                    current_letter_index = 0
                    wrong_presses = {}
        elif event.type == KEYDOWN and game_state == 'in_progress':
            if event.key == letter_to_key[letters[current_letter_index]]:
                key_center = get_key_center(letters[current_letter_index])
                fireworks.append({"center": key_center, "start_time": current_time})
                current_letter_index += 1
                if current_letter_index == 26:
                    game_state = 'finished'
                    final_time = (pygame.time.get_ticks() - start_time) / 1000.0
            elif event.key in key_to_letter:
                char = key_to_letter[event.key]
                wrong_presses[char] = pygame.time.get_ticks() + 2000

    screen.fill(BLACK)
    draw_quit_button(screen)
    
    if game_state == 'not_started':
        draw_start_button(screen)
        draw_keyboard(screen, None, wrong_presses, current_time)
        draw_coins(screen, current_letter_index, current_time)
    elif game_state == 'in_progress':
        elapsed_time = (current_time - start_time) / 1000.0
        draw_timer(screen, elapsed_time)
        draw_keyboard(screen, letters[current_letter_index], wrong_presses, current_time)
        draw_coins(screen, current_letter_index, current_time)
    elif game_state == 'finished':
        draw_keyboard(screen, None, wrong_presses, current_time)
        draw_final_message(screen, final_time)
        draw_coins(screen, current_letter_index, current_time)
        play_again_button = draw_play_again_button(screen)

    draw_fireworks(screen, current_time)
    pygame.display.flip()

pygame.quit()
