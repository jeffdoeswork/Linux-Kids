import pygame, random, math

# ----------------------
# Initialization
# ----------------------
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Number Clicking Game for Kids")
clock = pygame.time.Clock()

# ----------------------
# Fonts and Global Constants
# ----------------------
key_font = pygame.font.Font(None, 64)      # For numbers and buttons
message_font = pygame.font.Font(None, 80)   # For final message
timer_font = pygame.font.Font(None, 40)     # For timer display

BUBBLE_RADIUS = 40

# ----------------------
# Colors
# ----------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Bubble colors
BUBBLE_BG_INACTIVE = (100, 100, 100)   # dark gray
BUBBLE_TEXT_INACTIVE = (200, 200, 200) # light gray
BUBBLE_BG_ACTIVE = (173, 216, 230)       # light blue
BUBBLE_TEXT_ACTIVE = (255, 255, 255)     # white

# Button colors (reuse from your keyboard game)
GREEN = (0, 255, 0)
GRAYISH_RED = (150, 50, 50)

# For firework and coins
BRIGHT_YELLOW = (255, 255, 0)

# ----------------------
# Button Rectangles
# ----------------------
start_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 50, 200, 60)
quit_button = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 60)

# ----------------------
# Global Game Variables
# ----------------------
game_state = 'not_started'   # 'not_started', 'in_progress', 'finished'
bubbles = []                 # List of bubble dictionaries (each has "number", "pos", "fading", "fade_alpha")
current_active = 1           # Next number to click (1 to 10)
start_time = 0
final_time = 0
fireworks = []               # Each firework: {"center": (x,y), "start_time": ms}
coin_offsets = []            # For spinning coins (one per coin)

# ----------------------
# Helper Functions
# ----------------------
def create_bubbles():
    """
    Create bubbles for numbers 1-10 placed randomly within the window (leaving margins)
    and ensure that each bubble is at least 5 pixels apart from each other.
    """
    bubbles = []
    margin = 50
    min_distance = 2 * BUBBLE_RADIUS + 5  # Minimum center-to-center distance (bubble diameters + 5 pixels gap)
    for i in range(1, 11):
        valid = False
        attempts = 0
        while not valid and attempts < 1000:
            x = random.randint(margin + BUBBLE_RADIUS, SCREEN_WIDTH - margin - BUBBLE_RADIUS)
            y = random.randint(margin + BUBBLE_RADIUS + 100, SCREEN_HEIGHT - margin - BUBBLE_RADIUS - 100)
            valid = True
            for bubble in bubbles:
                bx, by = bubble["pos"]
                if math.hypot(x - bx, y - by) < min_distance:
                    valid = False
                    break
            attempts += 1
        # If after many attempts a valid position wasn't found, use the last position anyway.
        bubbles.append({"number": i, "pos": (x, y), "fading": False, "fade_alpha": 255})
    return bubbles

def draw_bubble(surface, bubble, is_active):
    """Draw a numbered bubble at its position. Active bubbles use light blue background with white text."""
    bubble_radius = BUBBLE_RADIUS
    # Choose colors based on active status
    if is_active:
        bg_color = BUBBLE_BG_ACTIVE
        text_color = BUBBLE_TEXT_ACTIVE
    else:
        bg_color = BUBBLE_BG_INACTIVE
        text_color = BUBBLE_TEXT_INACTIVE
    # If fading, use the bubble's current alpha
    alpha = bubble.get("fade_alpha", 255)
    # Create a temporary surface with per-pixel alpha
    bubble_surf = pygame.Surface((2*bubble_radius, 2*bubble_radius), pygame.SRCALPHA)
    color_with_alpha = (*bg_color, alpha)
    pygame.draw.circle(bubble_surf, color_with_alpha, (bubble_radius, bubble_radius), bubble_radius)
    # Render the number and set its transparency
    text = key_font.render(str(bubble["number"]), True, text_color)
    text.set_alpha(alpha)
    text_rect = text.get_rect(center=(bubble_radius, bubble_radius))
    bubble_surf.blit(text, text_rect)
    # Blit the bubble surface so that its center is at bubble["pos"]
    pos = bubble["pos"]
    surface.blit(bubble_surf, (pos[0] - bubble_radius, pos[1] - bubble_radius))

def draw_start_button(surface):
    pygame.draw.rect(surface, GREEN, start_button, border_radius=8)
    text = key_font.render("Start", True, BLACK)
    text_rect = text.get_rect(center=start_button.center)
    surface.blit(text, text_rect)

def draw_quit_button(surface):
    pygame.draw.rect(surface, GRAYISH_RED, quit_button, border_radius=8)
    text = key_font.render("Quit", True, WHITE)
    text_rect = text.get_rect(center=quit_button.center)
    surface.blit(text, text_rect)

def draw_play_again_button(surface):
    play_again_button = pygame.Rect((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT - 220, 300, 80)
    pygame.draw.rect(surface, GREEN, play_again_button, border_radius=8)
    text = key_font.render("Play Again?", True, BLACK)
    text_rect = text.get_rect(center=play_again_button.center)
    surface.blit(text, text_rect)
    return play_again_button

def draw_timer(surface, elapsed):
    text = timer_font.render(f"Time: {elapsed:.2f} s", True, WHITE)
    surface.blit(text, (20, 20))

def draw_final_message(surface, time_taken):
    text = message_font.render(f"Well Done! Time: {time_taken:.2f} sec", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 120))
    box_rect = text_rect.inflate(40, 30)
    pygame.draw.rect(surface, (50, 50, 50), box_rect)
    surface.blit(text, text_rect)

def draw_spinning_coin(surface, center, coin_radius, phase):
    # Cycle through 5 phases for a simple 3D spinning effect
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

def draw_coins(surface, num_coins, current_time):
    coin_radius = 20  # Size of each coin
    spacing = 10
    if num_coins > 0:
        total_width = num_coins * (2 * coin_radius) + (num_coins - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) / 2
        y = SCREEN_HEIGHT - (2 * coin_radius) - 40  # Bottom margin
        rotation_speed = 0.00314  # Radians per millisecond
        for i in range(num_coins):
            coin_center = (int(start_x + coin_radius + i * (2 * coin_radius + spacing)), int(y + coin_radius))
            coin_angle = coin_offsets[i] + current_time * rotation_speed
            phase = ((coin_angle + math.pi/2) % (2 * math.pi)) / (2 * math.pi)
            draw_spinning_coin(surface, coin_center, coin_radius, phase)

def draw_fireworks(surface, current_time):
    duration = 1500  # Duration of the firework in milliseconds
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
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    # ----- Event Handling -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if quit_button.collidepoint(mouse_pos):
                running = False

            if game_state == 'not_started':
                if start_button.collidepoint(mouse_pos):
                    game_state = 'in_progress'
                    bubbles = create_bubbles()
                    current_active = 1
                    start_time = current_time
                    # Initialize coin offsets for up to 10 coins
                    coin_offsets = [random.uniform(0, 2 * math.pi) for _ in range(10)]

            elif game_state == 'in_progress':
                # Look for the active bubble (with number == current_active) and check if it was clicked.
                for bubble in bubbles:
                    if bubble["number"] == current_active and not bubble["fading"]:
                        bx, by = bubble["pos"]
                        if math.hypot(mouse_pos[0] - bx, mouse_pos[1] - by) <= BUBBLE_RADIUS:
                            # Mark the bubble as fading and launch fireworks.
                            bubble["fading"] = True
                            bubble["fade_alpha"] = 255
                            fireworks.append({"center": bubble["pos"], "start_time": current_time})
                            if current_active < 10:
                                current_active += 1
                            else:
                                # When bubble 10 is clicked, finish the game.
                                game_state = 'finished'
                                final_time = (current_time - start_time) / 1000.0
                            break

            elif game_state == 'finished':
                play_again_button = pygame.Rect((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT - 220, 300, 80)
                if play_again_button.collidepoint(mouse_pos):
                    game_state = 'not_started'
                    bubbles = []
                    current_active = 1

    # ----- Update Fading Bubbles -----
    # For bubbles that are fading, decrement the fade_alpha and remove them if fully transparent.
    for bubble in bubbles[:]:
        if bubble["fading"]:
            bubble["fade_alpha"] -= 5  # Adjust fade speed as desired
            if bubble["fade_alpha"] <= 0:
                bubbles.remove(bubble)

    # ----- Drawing -----
    screen.fill(BLACK)
    draw_quit_button(screen)

    if game_state == 'not_started':
        draw_start_button(screen)

    elif game_state == 'in_progress':
        elapsed_time = (current_time - start_time) / 1000.0
        draw_timer(screen, elapsed_time)
        # Draw all bubbles (active bubble is drawn with active colors)
        for bubble in bubbles:
            is_active = (bubble["number"] == current_active) and (not bubble.get("fading", False))
            draw_bubble(screen, bubble, is_active)
        # Draw coins to represent points (one coin per successful click)
        draw_coins(screen, current_active - 1, current_time)

    elif game_state == 'finished':
        # Optionally, draw any remaining (fading) bubbles
        for bubble in bubbles:
            draw_bubble(screen, bubble, False)
        draw_final_message(screen, final_time)
        draw_coins(screen, current_active - 1, current_time)
        play_again_button = draw_play_again_button(screen)

    draw_fireworks(screen, current_time)
    pygame.display.flip()

pygame.quit()
