'''Coding ka Rule No. 1: If it runs, don't touch it hehe'''

import pygame
import random
import math
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_LEVEL = SCREEN_HEIGHT - 100

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Runner - Celestia")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
FOREST_GREEN = (34, 139, 34)
SEA_BLUE = (0, 105, 148)
SNOW_WHITE = (240, 240, 255)
SPACE_BLACK = (5, 5, 20)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3

# Font
font_small = pygame.font.SysFont("Arial", 20)
font_medium = pygame.font.SysFont("Arial", 30)
font_large = pygame.font.SysFont("Arial", 40)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Biomes
FOREST = 0
SEA = 1
SNOW = 2
SKY = 3
SPACE = 4
biome_names = ["Forest", "Sea", "Snow", "Sky", "Space"]
biome_music = {
    FOREST: "On.mp3",
    SEA: "All Over.mp3",
    SNOW: "Snow.mp3",
    SKY: "Glory.mp3",
    SPACE: "Galaxial.mp3"
}

#resource path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#directories
current_dir = os.path.dirname(__file__)
bgm_path = os.path.join(current_dir, "assets", "music")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = GROUND_LEVEL - self.rect.height
        self.velocity_y = 0
        self.jumping = False
        self.is_alive = True
        self.frame = 0
        self.animation_cooldown = 5
        self.animation_frames = 8
        self.animation_timer = 0

    def update(self, obstacles, coins):
        # Gravity
        if self.jumping:
            self.velocity_y += 0.8
            self.rect.y += self.velocity_y
            
            # Check if landed
            if self.rect.y >= GROUND_LEVEL - self.rect.height:
                self.rect.y = GROUND_LEVEL - self.rect.height
                self.jumping = False
                self.velocity_y = 0

        # Collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.is_alive = False
                
        # Collect coins
        for coin in list(coins):
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                return 1
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_cooldown:
            self.frame = (self.frame + 1) % self.animation_frames
            self.animation_timer = 0
            
        return 0

    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed
        self.type = random.randint(0, 3)  # 0: gap, 1: vehicle/animal, 2: wall, 3: biome specific
        
        if self.type == 0:  # Gap
            self.image = pygame.Surface((80, 15))
            self.image.fill(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - 5
        elif self.type == 1:  # Vehicle/animal
            self.image = pygame.Surface((50, 30))
            if biome == FOREST:
                self.image.fill(FOREST_GREEN)  # Animal
            elif biome == SEA:
                self.image.fill(SEA_BLUE)  # Sea creature
            elif biome == SNOW:
                self.image.fill(WHITE)  # Polar bear
            elif biome == SKY:
                self.image.fill(SKY_BLUE)  # Bird
            else:
                self.image.fill(RED)  # UFO
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - self.rect.height
        elif self.type == 2:  # Wall/barricade
            self.image = pygame.Surface((40, 60))
            self.image.fill(RED)
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - self.rect.height
        else:  # Biome specific
            if biome == FOREST:
                # Log or rock
                height = random.randint(30, 50)
                self.image = pygame.Surface((40, height))
                self.image.fill((139, 69, 19))  # Brown
                self.rect = self.image.get_rect()
                self.rect.x = SCREEN_WIDTH
                self.rect.y = GROUND_LEVEL - height
            elif biome == SEA:
                # Tentacle
                height = random.randint(50, 100)
                self.image = pygame.Surface((20, height))
                self.image.fill((128, 0, 128))  # Purple
                self.rect = self.image.get_rect()
                self.rect.x = SCREEN_WIDTH
                self.rect.y = GROUND_LEVEL - height
            elif biome == SNOW:
                # Boulder
                size = random.randint(30, 50)
                self.image = pygame.Surface((size, size))
                self.image.fill((200, 200, 200))  # Light gray
                self.rect = self.image.get_rect()
                self.rect.x = SCREEN_WIDTH
                self.rect.y = GROUND_LEVEL - size
            elif biome == SKY:
                # Cloud
                width = random.randint(60, 100)
                height = random.randint(30, 50)
                self.image = pygame.Surface((width, height))
                self.image.fill((220, 220, 220))  # Light gray
                self.rect = self.image.get_rect()
                self.rect.x = SCREEN_WIDTH
                self.rect.y = GROUND_LEVEL - random.randint(50, 150)
            else:  # SPACE
                # Asteroid
                size = random.randint(20, 40)
                self.image = pygame.Surface((size, size))
                self.image.fill((169, 169, 169))  # Gray
                self.rect = self.image.get_rect()
                self.rect.x = SCREEN_WIDTH
                self.rect.y = GROUND_LEVEL - random.randint(20, 100)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            return True
        return False

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(GROUND_LEVEL - 150, GROUND_LEVEL - 30)
        self.speed = speed
        self.angle = 0

    def update(self):
        self.rect.x -= self.speed
        
        # Coin spinning animation
        self.angle = (self.angle + 5) % 360
        
        if self.rect.right < 0:
            return True
        return False

# Background elements for each biome
class BackgroundElement(pygame.sprite.Sprite):
    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed * 0.5  # Background moves slower than obstacles
        
        if biome == FOREST:
            # Tree
            width = random.randint(30, 60)
            height = random.randint(100, 200)
            self.image = pygame.Surface((width, height))
            self.image.fill((34, 139, 34))  # Forest green
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - height
        elif biome == SEA:
            # Coral
            width = random.randint(20, 40)
            height = random.randint(30, 80)
            self.image = pygame.Surface((width, height))
            self.image.fill((255, 127, 80))  # Coral color
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - height
        elif biome == SNOW:
            # Snow-covered tree
            width = random.randint(30, 50)
            height = random.randint(80, 150)
            self.image = pygame.Surface((width, height))
            self.image.fill((200, 200, 255))  # Light blue-white
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = GROUND_LEVEL - height
        elif biome == SKY:
            # Cloud
            width = random.randint(60, 120)
            height = random.randint(20, 50)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 255, 255, 150), (0, 0, width, height))
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(50, GROUND_LEVEL - 150)
        else:  # SPACE
            # Star
            self.image = pygame.Surface((3, 3))
            self.image.fill(WHITE)
            self.rect = self.image.get_rect()
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(10, GROUND_LEVEL - 10)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            return True
        return False

#Background music initialization
pygame.mixer.init()

# Game class
class Game:
    def __init__(self):
        self.reset_game()
        self.current_music_biome = None  # to keep track of current biome's music
        
    def reset_game(self):
        self.game_state = MENU
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.bg_elements = []
        self.score = 0
        self.speed = 5
        self.obstacle_timer = 0
        self.obstacle_cooldown = 100
        self.coin_timer = 0
        self.coin_cooldown = 150
        self.bg_element_timer = 0
        self.bg_element_cooldown = 50
        self.biome = FOREST
        self.biome_change_score = 200
        self.ground_color = FOREST_GREEN
        self.sky_color = SKY_BLUE
        
    def run(self):
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if self.game_state == MENU:
                        if event.key == pygame.K_RETURN:
                            self.game_state = PLAYING
                        elif event.key == pygame.K_i:
                            self.game_state = INSTRUCTIONS
                    
                    elif self.game_state == INSTRUCTIONS:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_BACKSPACE:
                            self.game_state = MENU
                    
                    elif self.game_state == PLAYING:
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                    
                    elif self.game_state == GAME_OVER:
                        if event.key == pygame.K_RETURN:
                            self.reset_game()
                            self.game_state = PLAYING
                        elif event.key == pygame.K_BACKSPACE:
                            self.reset_game()
            
            # Game state handling
            if self.game_state == MENU:
                self.draw_menu()
            elif self.game_state == INSTRUCTIONS:
                self.draw_instructions()
            elif self.game_state == PLAYING:
                self.update()
                self.draw()
            elif self.game_state == GAME_OVER:
                self.draw_game_over()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def update(self):
        # Check if player is alive
        if not self.player.is_alive:
            self.game_state = GAME_OVER
            return
            
        # Update player
        coins_collected = self.player.update(self.obstacles, self.coins)
        self.score += coins_collected
        
        # Increase speed gradually
        self.speed = min(15, 5 + (self.score / 500))
        
                # Update biome
        if self.score >= self.biome_change_score:
            self.biome = (self.biome + 1) % 5
            self.biome_change_score += 50

        # Change ground and sky colors
        if self.biome == FOREST:
            self.ground_color = FOREST_GREEN
            self.sky_color = SKY_BLUE
        elif self.biome == SEA:
            self.ground_color = SEA_BLUE
            self.sky_color = (173, 216, 230)
        elif self.biome == SNOW:
            self.ground_color = SNOW_WHITE
            self.sky_color = (200, 200, 255)
        elif self.biome == SKY:
            self.ground_color = (135, 206, 250)
            self.sky_color = (0, 191, 255)
        else:  # SPACE
            self.ground_color = (50, 50, 50)
            self.sky_color = SPACE_BLACK

        # Change music if biome changed
        if self.current_music_biome != self.biome:
            music_file = biome_music.get(self.biome)
            if music_file:
                pygame.mixer.music.load(resource_path(os.path.join(bgm_path, music_file)))
                pygame.mixer.music.set_volume(1.0)
                pygame.mixer.music.play(-1)
            self.current_music_biome = self.biome

        
        # Add new obstacle
        self.obstacle_timer += 1
        if self.obstacle_timer >= self.obstacle_cooldown:
            self.obstacles.append(Obstacle(self.biome, self.speed))
            self.obstacle_timer = 0
            self.obstacle_cooldown = random.randint(80, 150)
        
        # Add new coin
        self.coin_timer += 1
        if self.coin_timer >= self.coin_cooldown:
            self.coins.append(Coin(self.speed))
            self.coin_timer = 0
            self.coin_cooldown = random.randint(100, 200)
        
        # Add new background element
        self.bg_element_timer += 1
        if self.bg_element_timer >= self.bg_element_cooldown:
            self.bg_elements.append(BackgroundElement(self.biome, self.speed))
            self.bg_element_timer = 0
            self.bg_element_cooldown = random.randint(30, 80)
        
        # Update obstacles and remove if off-screen
        for obstacle in list(self.obstacles):
            if obstacle.update():
                self.obstacles.remove(obstacle)
        
        # Update coins and remove if off-screen
        for coin in list(self.coins):
            if coin.update():
                self.coins.remove(coin)
        
        # Update background elements and remove if off-screen
        for bg_element in list(self.bg_elements):
            if bg_element.update():
                self.bg_elements.remove(bg_element)
        
        # Increase score over time
        self.score += 0.1
    
    def draw(self):
        # Draw background based on biome
        screen.fill(self.sky_color)
        
        # Draw background elements
        for bg_element in self.bg_elements:
            screen.blit(bg_element.image, bg_element.rect)
        
        # Draw ground
        pygame.draw.rect(screen, self.ground_color, (0, GROUND_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_LEVEL))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        
        # Draw coins
        for coin in self.coins:
            screen.blit(coin.image, coin.rect)
        
        # Draw player
        screen.blit(self.player.image, self.player.rect)
        
        # Draw score
        score_text = font_medium.render(f"Score: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw current biome
        biome_text = font_small.render(f"Biome: {biome_names[self.biome]}", True, WHITE)
        screen.blit(biome_text, (10, 40))
    
    def draw_menu(self):
        screen.fill(SPACE_BLACK)
        
        # Draw stars
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Draw title
        title_text = font_large.render("COSMIC RUNNER", True, YELLOW)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw start prompt
        start_text = font_medium.render("Press ENTER to Start", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 250))
        
        # Draw instructions prompt
        inst_text = font_medium.render("Press I for Instructions", True, WHITE)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 300))
        
        # Draw animation
        pygame.draw.rect(screen, ORANGE, (SCREEN_WIDTH // 2 - 15, 400, 30, 50))
        
        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, GROUND_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_LEVEL))
    
    def draw_instructions(self):
        screen.fill(SPACE_BLACK)
        
        # Draw title
        title_text = font_large.render("Instructions", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Draw instructions
        inst_lines = [
            "- Press SPACE to jump over obstacles",
            "- Collect coins to increase your score",
            "- Avoid obstacles (gaps, animals, walls, etc.)",
            "- Biomes change as you progress:",
            "    Forest -> Sea -> Snow -> Sky -> Space",
            "- Each biome has unique obstacles and background",
            "- The game gets faster as your score increases"
            "- Survive as long as possible!"
        ]
        
        for i, line in enumerate(inst_lines):
            line_text = font_small.render(line, True, WHITE)
            screen.blit(line_text, (100, 150 + i * 40))
        
        # Draw return prompt
        return_text = font_medium.render("Press ENTER to return to menu", True, WHITE)
        screen.blit(return_text, (SCREEN_WIDTH // 2 - return_text.get_width() // 2, 500))
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        # Draw score
        score_text = font_medium.render(f"Your score: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        # Draw restart prompt
        restart_text = font_medium.render("Press ENTER to play again", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
        
        # Draw menu prompt
        menu_text = font_medium.render("Press BACKSPACE to return to menu", True, WHITE)
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 400))

# Main function
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
