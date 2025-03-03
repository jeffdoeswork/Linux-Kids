import pygame
import random
import math

pygame.init()

# --------------------------
# CONFIGURATION & CONSTANTS
# --------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GRAVITY = 0.8
JUMP_VELOCITY = -15
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Ground level (top of floor platform)
GROUND_Y = SCREEN_HEIGHT - 20

# Colors
BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
BLUE    = (0, 0, 255)
YELLOW  = (255, 255, 0)
GREEN   = (0, 255, 0)

# --------------------------
# HELPER FUNCTION
# --------------------------
def draw_star(size, color):
    """
    Returns a Surface with a centered five-pointed star.
    """
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size / 2, size / 2
    outer_r = size / 2
    inner_r = outer_r * 0.5
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)
    return surface

# --------------------------
# SPRITE CLASSES
# --------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        # Align player's bottom to ground.
        self.rect.bottom = GROUND_Y
        self.vel_y = 0
        self.speed = PLAYER_SPEED
        self.score = 0
        self.lives = 3
        self.coins = 0

    def update(self, platforms, enemies):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed

        # --- HORIZONTAL MOVEMENT ---
        self.rect.x += dx
        # Resolve horizontal collisions
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                elif dx < 0:
                    self.rect.left = plat.rect.right

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # --- VERTICAL MOVEMENT ---
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        # Resolve vertical collisions
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                # Falling: snap to platform top
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                # Jumping: stop upward movement
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0

        # --- ENEMY COLLISION ---
        hit_enemy = pygame.sprite.spritecollideany(self, enemies)
        if hit_enemy:
            if self.vel_y > 0 and abs(self.rect.bottom - hit_enemy.rect.top) < 20:
                hit_enemy.kill()
                self.score += 10
                self.vel_y = JUMP_VELOCITY
            else:
                self.lives -= 1
                self.respawn()

    def jump(self):
        if self.vel_y == 0:
            self.vel_y = JUMP_VELOCITY

    def respawn(self):
        self.rect.x = 50
        self.rect.bottom = GROUND_Y
        self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = GROUND_Y
        self.speed = ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = draw_star(30, GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --------------------------
# LEVEL CREATION
# --------------------------
def create_level(level):
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # Ground platform
    ground = Platform(0, GROUND_Y, SCREEN_WIDTH)
    platforms.add(ground)

    if level == 1:
        platforms.add(Platform(200, 450, 150))
        platforms.add(Platform(400, 350, 150))
        coins.add(Coin(250, 420), Coin(450, 320))
        enemies.add(Enemy(300))
        stars.add(Star(SCREEN_WIDTH - 60, GROUND_Y - 30))
    elif level == 2:
        # Lower floating platforms so they are reachable.
        platforms.add(Platform(150, 520, 100))   # 60 pixels above ground
        platforms.add(Platform(350, 460, 100))   # 120 pixels above ground
        platforms.add(Platform(550, 400, 80))    # 180 pixels above ground
        # Place coins on these platforms (30 pixels above platform top)
        coins.add(Coin(180, 520 - 30), Coin(380, 460 - 30), Coin(580, 400 - 30))
        enemies.add(Enemy(200), Enemy(500))
        # Place the star on the third platform; shift it horizontally to avoid overlap with coin.
        stars.add(Star(600, 400 - 30))
    elif level == 3:
        platforms.add(Platform(100, 450, 80))
        platforms.add(Platform(300, 350, 150))
        platforms.add(Platform(550, 270, 100))
        coins.add(Coin(110, 420), Coin(350, 320), Coin(580, 240))
        enemies.add(Enemy(120), Enemy(400), Enemy(600))
        stars.add(Star(700, 240))

    return platforms, enemies, coins, stars

# --------------------------
# MAIN GAME LOOP
# --------------------------
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Platformer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    player = Player(50)
    level = 1
    platforms, enemies, coins, stars = create_level(level)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(platforms, enemies, coins, stars, player)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        player.update(platforms, enemies)
        enemies.update()

        # Collect coins
        collected = pygame.sprite.spritecollide(player, coins, True)
        for _ in collected:
            player.coins += 1
            player.score += 5

        # Collect star to advance level
        if pygame.sprite.spritecollide(player, stars, True):
            level += 1
            if level > 3:
                running = False
            else:
                platforms, enemies, coins, stars = create_level(level)
                all_sprites.empty()
                all_sprites.add(platforms, enemies, coins, stars, player)
                player.respawn()

        if player.rect.top >= SCREEN_HEIGHT:
            player.lives -= 1
            player.respawn()
            if player.lives <= 0:
                running = False

        screen.fill(BLACK)
        all_sprites.draw(screen)

        score_surf = font.render(f"Score: {player.score}", True, WHITE)
        lives_surf = font.render(f"Lives: {player.lives}", True, WHITE)
        coins_surf = font.render(f"Coins: {player.coins}", True, WHITE)
        level_surf = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_surf, (10, 10))
        screen.blit(lives_surf, (10, 40))
        screen.blit(coins_surf, (10, 70))
        screen.blit(level_surf, (10, 100))

        pygame.display.flip()

    screen.fill(BLACK)
    if level > 3:
        msg = font.render("Congratulations! You finished all levels!", True, WHITE)
    else:
        msg = font.render(f"Game Over! Final Score: {player.score}", True, WHITE)
    screen.blit(msg, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()
