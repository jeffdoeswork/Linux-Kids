import pygame
from pygame.locals import *
import random
import string

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Keyboard Learning Game for Kids")

# Define Colors
BLACK = (0, 0, 0)
DULL_GRAY = (100, 100, 100)
BRIGHT_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAYISH_RED = (150, 50, 50)

# Set Up Fonts
key_font = pygame.font.Font(None, 36)  # For key characters
message_font = pygame.font.Font(None, 48)  # For final message
timer_font = pygame.font.Font(None, 24)  # For timer display

# Define Keyboard Rows
rows = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],  # First row: 1 to 0
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],  # Second row: Q to P
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],       # Third row: A to L
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']                 # Fourth row: Z to M
]

# List of All 26 Letters for the Game
letters = list(string.ascii_uppercase)  # 'A' to 'Z'

# Map Letters to Pygame Key Constants and Vice Versa
letter_to_key = {chr(ord('A') + i): globals()['K_' + chr(ord('a') + i)] for i in range(26)}
key_to_letter = {globals()['K_' + chr(ord('a') + i)]: chr(ord('A') + i) for i in range(26)}

# Game State Variables
game_state = 'not_started'
current_letter_index = 0
start_time = 0
final_time = 0
wrong_presses = {}

# Start Button Rectangle
start_button = pygame.Rect(350, 100, 100, 50)

# Function to Draw a Single Key with Background and Text Color
def draw_key(surface, x, y, character, bg_color, text_color):
    key_rect = pygame.Rect(x, y, 50, 50)
    pygame.draw.rect(surface, bg_color, key_rect)
    text = key_font.render(character, True, text_color)
    text_rect = text.get_rect(center=key_rect.center)
    surface.blit(text, text_rect)

# Function to Draw the Entire Keyboard with Highlight and Wrong Press Effects
def draw_keyboard(surface, highlighted_letter, wrong_presses, current_time):
    for row_idx, row in enumerate(rows):
        row_width = len(row) * 50 + (len(row) - 1) * 10
        start_x = (800 - row_width) / 2
        y = 200 + row_idx * 70
        for i, char in enumerate(row):
            x = start_x + i * 60
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

# Function to Draw the Start Button
def draw_start_button(surface):
    pygame.draw.rect(surface, GREEN, start_button)
    text = key_font.render("Start", True, BLACK)
    text_rect = text.get_rect(center=start_button.center)
    surface.blit(text, text_rect)

# Function to Draw the Timer
def draw_timer(surface, elapsed):
    text = timer_font.render(f"Time: {elapsed:.2f} s", True, WHITE)
    surface.blit(text, (10, 10))

# Function to Draw the Final Message with a Background Box
def draw_final_message(surface, time_taken):
    text = message_font.render(f"Well Done! Time: {time_taken:.2f} seconds!", True, WHITE)
    text_rect = text.get_rect(center=(800 // 2, 50))
    box_rect = text_rect.inflate(20, 10)
    pygame.draw.rect(surface, (50, 50, 50), box_rect)
    surface.blit(text, text_rect)

# Function to Draw Coins for Correct Presses
def draw_coins(surface, num_coins):
    for i in range(num_coins):
        x = 10 + i * 30
        y = 10
        pygame.draw.circle(surface, BRIGHT_YELLOW, (x + 10, y + 10), 10)

# Main Game Loop
running = True
while running:
    # Handle Events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and game_state == 'not_started':
            if start_button.collidepoint(event.pos):
                random.shuffle(letters)  # Randomize letter order
                current_letter_index = 0
                start_time = pygame.time.get_ticks()
                game_state = 'in_progress'
                wrong_presses = {}  # Reset wrong presses
        elif event.type == KEYDOWN and game_state == 'in_progress':
            if event.key == letter_to_key[letters[current_letter_index]]:
                current_letter_index += 1
                if current_letter_index == 26:  # All letters pressed
                    game_state = 'finished'
                    final_time = (pygame.time.get_ticks() - start_time) / 1000.0
            elif event.key in key_to_letter:
                char = key_to_letter[event.key]
                wrong_presses[char] = pygame.time.get_ticks() + 2000

    # Clear Screen
    screen.fill(BLACK)

    # Get Current Time for Fade Effects
    current_time = pygame.time.get_ticks()

    # Draw Based on Game State
    if game_state == 'not_started':
        draw_start_button(screen)
        draw_keyboard(screen, None, wrong_presses, current_time)
        draw_coins(screen, current_letter_index)
    elif game_state == 'in_progress':
        elapsed_time = (current_time - start_time) / 1000.0
        draw_timer(screen, elapsed_time)
        draw_keyboard(screen, letters[current_letter_index], wrong_presses, current_time)
        draw_coins(screen, current_letter_index)
    elif game_state == 'finished':
        draw_keyboard(screen, None, wrong_presses, current_time)
        draw_final_message(screen, final_time)
        draw_coins(screen, current_letter_index)

    # Update Display
    pygame.display.flip()

# Clean Up
pygame.quit()
