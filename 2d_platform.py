import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
GRAVITY = 0.8
JUMP_VEL = -15
PLAYER_SPEED = 5

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Adventure")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT - 100
        self.vel_y = 0
        self.lives = 3
        self.score = 0
        self.speed = PLAYER_SPEED

    def update(self, platforms, enemies):
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            
        # Screen boundaries
        self.rect.clamp_ip(screen.get_rect())
        
        # Platform collision
        platform_hit = pygame.sprite.spritecollideany(self, platforms)
        if platform_hit and self.vel_y > 0:
            self.rect.bottom = platform_hit.rect.top
            self.vel_y = 0
            
        # Enemy collision
        enemy_hit = pygame.sprite.spritecollideany(self, enemies)
        if enemy_hit:
            if self.vel_y > 0 and self.rect.bottom - enemy_hit.rect.top < 20:
                enemy_hit.kill()
                self.score += 10
                self.vel_y = JUMP_VEL
            else:
                self.lives -= 1
                self.rect.x = 50
                self.rect.y = HEIGHT - 100

    def jump(self):
        if self.vel_y == 0:
            self.vel_y = JUMP_VEL

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        pygame.draw.star(self.image, (0, 255, 0), (12, 12), 12, 5)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_level(level_num):
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Ground
    platforms.add(Platform(0, HEIGHT - 20, WIDTH))
    
    if level_num == 1:
        platforms.add(Platform(200, 400, 150))
        platforms.add(Platform(400, 300, 150))
        coins.add(Coin(250, 360), Coin(450, 260))
        enemies.add(Enemy(300, HEIGHT - 50))
        
    elif level_num == 2:
        platforms.add(Platform(150, 450, 100), Platform(300, 350, 100),
                     Platform(450, 250, 100))
        coins.add(Coin(200, 410), Coin(350, 310), Coin(500, 210))
        enemies.add(Enemy(200, HEIGHT - 50), Enemy(400, HEIGHT - 50))
        powerups.add(PowerUp(475, 220))
        
    elif level_num == 3:
        platforms.add(Platform(100, 500, 80), Platform(250, 400, 80),
                     Platform(400, 300, 80), Platform(550, 200, 80))
        coins.add(Coin(130, 460), Coin(280, 360), Coin(430, 260), Coin(580, 160))
        enemies.add(Enemy(150, HEIGHT - 50), Enemy(300, HEIGHT - 50),
                   Enemy(450, HEIGHT - 50))
        powerups.add(PowerUp(580, 170))
        
    return platforms, coins, enemies, powerups

def main():
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    level = 1
    platforms, coins, enemies, powerups = create_level(level)
    all_sprites.add(platforms, coins, enemies, powerups)
    
    font = pygame.font.Font(None, 36)
    running = True
    level_complete = False
    coins_needed = 10  # Points needed to advance (2 coins)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
            if event.type == pygame.USEREVENT:
                player.speed = PLAYER_SPEED
        
        # Update
        all_sprites.update(platforms, enemies)
        
        # Collect coins
        collected = pygame.sprite.spritecollide(player, coins, True)
        for coin in collected:
            player.score += 5
        
        # Collect power-ups
        if pygame.sprite.spritecollide(player, powerups, True):
            player.speed = PLAYER_SPEED * 1.5
            pygame.time.set_timer(pygame.USEREVENT, 5000)  # 5 sec power-up
        
        # Check for pitfall
        if player.rect.y > HEIGHT:
            player.lives -= 1
            player.rect.x = 50
            player.rect.y = HEIGHT - 100
            if player.lives <= 0:
                running = False
        
        # Level completion check
        if not coins and not enemies and not level_complete:
            level_complete = True
            level += 1
            if level > 3:
                running = False  # Game completed
            else:
                # Reset player position
                player.rect.x = 50
                player.rect.y = HEIGHT - 100
                # Create new level
                platforms.empty()
                coins.empty()
                enemies.empty()
                powerups.empty()
                platforms, coins, enemies, powerups = create_level(level)
                all_sprites.empty()
                all_sprites.add(player, platforms, coins, enemies, powerups)
                level_complete = False
                coins_needed += 5  # Increase difficulty
        
        # Draw
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        
        # HUD
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(level_text, (10, 70))
        
        pygame.display.flip()
        clock.tick(60)

    # Game over/win message
    screen.fill((0, 0, 0))
    final_text = font.render(f"Game Over - Final Score: {player.score}", True, WHITE)
    if level > 3:
        final_message = font.render("Congratulations! You Won!", True, WHITE)
    screen.blit(final_text, (WIDTH//2 - 100, HEIGHT//2 - 20))
    if level > 3:
        screen.blit(final_message, (WIDTH//2 - 120, HEIGHT//2 + 20))
    pygame.display.flip()
    pygame.time.wait(2000)
    
    pygame.quit()

if __name__ == "__main__":
    main()