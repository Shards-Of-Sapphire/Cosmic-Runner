import pygame
import random
import math
import sys
import os
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_LEVEL = SCREEN_HEIGHT - 100

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Cosmic Runner")

# Track window state
is_fullscreen = False
windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)


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
MOON_COLOR = (220, 220, 220)  # Light gray for moon
SUN_COLOR = (255, 215, 0)  # Gold for sun

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3
PAUSED = 4

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

# Time of day
DAY = 0
NIGHT = 1

# Tile size
TILE_SIZE = 32


# Window controls function
def toggle_fullscreen():
    global screen, is_fullscreen, windowed_size, SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL
    # ...existing code...
    
    if is_fullscreen:
        # Return to windowed mode
        screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
        SCREEN_WIDTH, SCREEN_HEIGHT = windowed_size
        is_fullscreen = False
    else:
        # Save current window size before going fullscreen
        windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        # Switch to fullscreen
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        is_fullscreen = True
    
    # Update ground level based on new screen height
    GROUND_LEVEL = SCREEN_HEIGHT - 100

def minimize_window():
    pygame.display.iconify()

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
            self.image = pygame.Surface((80, 20))
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
    
# Checkpoint class
class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed
        
        # Define checkpoint size and appearance
        self.width = 30
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Different appearance for each biome
        if biome == FOREST:
            self.color = (50, 200, 50)  # Bright green
            self.symbol = "F"
        elif biome == SEA:
            self.color = (50, 50, 200)  # Bright blue
            self.symbol = "S"
        elif biome == SNOW:
            self.color = (200, 200, 255)  # Light blue-white
            self.symbol = "N"
        elif biome == SKY:
            self.color = (100, 200, 255)  # Sky blue
            self.symbol = "K"
        else:  # SPACE
            self.color = (200, 100, 200)  # Purple
            self.symbol = "P"
        
        # Draw the checkpoint flag
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, self.width, self.height), 2)  # White border
        
        # Draw the pole
        pygame.draw.rect(self.image, (150, 75, 0), (0, 0, 5, self.height))  # Brown pole
        
        # Add the biome symbol
        font = pygame.font.SysFont("Arial", 18)
        symbol_text = font.render(self.symbol, True, (0, 0, 0))
        self.image.blit(symbol_text, (self.width//2 - symbol_text.get_width()//2, self.height//2 - symbol_text.get_height()//2))
        
        # Set position
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = GROUND_LEVEL - self.height
        
        # Animation attributes
        self.animation_counter = 0
        self.wave_amplitude = 3
        
    def update(self):
        self.rect.x -= self.speed
        
        # Waving flag animation
        self.animation_counter += 0.1
        wave = math.sin(self.animation_counter) * self.wave_amplitude
        
        # Recreate the image with waving effect
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the pole
        pygame.draw.rect(self.image, (150, 75, 0), (0, 0, 5, self.height))  # Brown pole
        
        # Draw the waving flag
        points = [
            (5, 5),
            (self.width, 5 + wave),
            (self.width, 25 + wave),
            (5, 25)
        ]
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, (255, 255, 255), points, 1)  # White border
        
        # Add the biome symbol
        font = pygame.font.SysFont("Arial", 12)
        symbol_text = font.render(self.symbol, True, (0, 0, 0))
        self.image.blit(symbol_text, (10, 10))
        
        # Return True if off-screen
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

# Sun/Moon class for day/night cycle
class CelestialBody(pygame.sprite.Sprite):
    def __init__(self, time_of_day, biome):
        super().__init__()
        self.time_of_day = time_of_day
        self.biome = biome
        
        # Size varies by biome
        if biome == SPACE:
            self.size = 30  # Smaller in space
        else:
            self.size = 50  # Normal size elsewhere
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw sun or moon based on time_of_day
        if time_of_day == DAY:
            # Draw sun
            pygame.draw.circle(self.image, SUN_COLOR, (self.size // 2, self.size // 2), self.size // 2)
            # Add rays for sun in non-space biomes
            if biome != SPACE:
                for i in range(8):
                    angle = math.radians(i * 45)  # 8 rays evenly spaced
                    start_x = self.size // 2 + (self.size // 2) * math.cos(angle)
                    start_y = self.size // 2 + (self.size // 2) * math.sin(angle)
                    end_x = self.size // 2 + (self.size // 1.2) * math.cos(angle)
                    end_y = self.size // 2 + (self.size // 1.2) * math.sin(angle)
                    pygame.draw.line(self.image, SUN_COLOR, (start_x, start_y), (end_x, end_y), 3)
        else:
            # Draw moon
            pygame.draw.circle(self.image, MOON_COLOR, (self.size // 2, self.size // 2), self.size // 2)
            # Add crater details for moon
            for _ in range(5):
                crater_size = random.randint(3, 7)
                crater_x = random.randint(10, self.size - 10)
                crater_y = random.randint(10, self.size - 10)
                pygame.draw.circle(self.image, (180, 180, 180), (crater_x, crater_y), crater_size)
        
        self.rect = self.image.get_rect()
        
        # Position based on biome
        if biome == SPACE:
            # In space, can be anywhere
            self.rect.x = random.randint(100, SCREEN_WIDTH - 100)
            self.rect.y = random.randint(50, GROUND_LEVEL - 100)
        else:
            # For other biomes, in the sky
            self.rect.x = SCREEN_WIDTH - 100
            self.rect.y = 80
        
        # Animation attributes
        self.angle = 0
        self.radius = 0
        self.center_x = self.rect.x
        self.center_y = self.rect.y
        
        # For space biome, have some movement
        if biome == SPACE:
            self.speed_x = random.uniform(-0.5, 0.5)
            self.speed_y = random.uniform(-0.5, 0.5)
        else:
            # For other biomes, slowly move across the sky
            self.speed_x = -0.2
            self.speed_y = 0
    
    def update(self):
        if self.biome == SPACE:
            # In space, slight random movement
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            # Change direction occasionally
            if random.random() < 0.01:
                self.speed_x = random.uniform(-0.5, 0.5)
                self.speed_y = random.uniform(-0.5, 0.5)
                
            # Keep within screen bounds
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.speed_x *= -1
            if self.rect.top < 0 or self.rect.bottom > GROUND_LEVEL:
                self.speed_y *= -1
        else:
            # For other biomes, arc movement across the sky
            self.rect.x += self.speed_x
            
            # When off-screen, reset position
            if self.rect.right < 0:
                self.rect.x = SCREEN_WIDTH
            
            # Adjust height based on x position to create arc
            # Create a slight arc effect
            relative_x = (self.rect.x % SCREEN_WIDTH) / SCREEN_WIDTH
            arc_height = 40  # Maximum height variation
            self.rect.y = 80 + math.sin(relative_x * math.pi) * arc_height

class Mission:
    def __init__(self, biome, difficulty_multiplier=1.0):
        self.completed = False
        self.biome = biome
        self.time_created = time.time()
        self.coins_collected = 0
        self.obstacles_avoided = 0
        self.time_survived = 0
        
        # Apply difficulty scaling based on biome level and multiplier
        self.difficulty = (biome + 1) * difficulty_multiplier
        
        # Generate random mission based on biome
        # Higher biomes have chance for harder mission types
        if biome >= 3:  # Sky or Space biomes
            mission_types = ["collect", "avoid", "survive", "perfect", "speed"]
        else:
            mission_types = ["collect", "avoid", "survive"]
        self.mission_type = random.choice(mission_types)
        
        # Set mission parameters based on type and biome - harder with progression
        if self.mission_type == "collect":
            self.target_amount = int(random.randint(8, 15) * self.difficulty)  # Much more coins required
            self.description = f"HARD: Collect {self.target_amount} coins in the {biome_names[biome]} biome"
        elif self.mission_type == "avoid":
            self.target_amount = int(random.randint(12, 20) * self.difficulty)  # More obstacles
            self.description = f"HARD: Avoid {self.target_amount} obstacles in the {biome_names[biome]} biome"
        elif self.mission_type == "survive":
            self.target_amount = int(random.randint(30, 60) * self.difficulty)  # Longer survival
            self.description = f"HARD: Survive {self.target_amount} seconds in the {biome_names[biome]} biome"
        elif self.mission_type == "perfect":
            # Perfect run - no hits for a certain distance/time
            self.target_amount = int(random.randint(45, 90) * self.difficulty)  # Seconds without hits
            self.description = f"EXTREME: Perfect run for {self.target_amount} seconds in {biome_names[biome]}"
        else:  # speed
            # Speed run - reach certain score within time limit
            self.target_amount = int(random.randint(300, 600) * self.difficulty)  # Score to reach
            self.time_limit = int(random.randint(30, 60))  # Seconds to reach it
            self.description = f"EXTREME: Score {self.target_amount} points in {self.time_limit}s in {biome_names[biome]}"
        
        # Set reward based on difficulty (biome level and target amount)
        base_reward = 100
        biome_multiplier = biome + 2  # Higher base multiplier
        target_factor = self.target_amount / 10
        
        # Higher rewards for harder mission types
        if self.mission_type in ["perfect", "speed"]:
            base_reward = 250  # Much higher base reward for extreme missions
        
        self.reward = int(base_reward * biome_multiplier * target_factor * difficulty_multiplier)
    
    def update(self, current_biome, delta_coins=0, delta_obstacles=0, delta_time=1/60, 
               player_hit=False, current_score=0):
        """Update mission progress with expanded parameters"""
        # Only update if in the correct biome
        if current_biome != self.biome:
            return False
            
        # Update appropriate counters
        if self.mission_type == "collect":
            self.coins_collected += delta_coins
            if self.coins_collected >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "avoid":
            self.obstacles_avoided += delta_obstacles
            if self.obstacles_avoided >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "survive":
            self.time_survived += delta_time
            if self.time_survived >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "perfect":
            # For perfect run: fail if player hit an obstacle
            if player_hit:
                # Failed perfect run, create a new mission
                return False
            
            self.time_survived += delta_time
            if self.time_survived >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "speed":
            # For speed run: check if score reached within time limit
            self.time_survived += delta_time
            
            if current_score >= self.target_amount:
                self.completed = True
                return True
                
            # Fail if time limit exceeded
            if self.time_survived >= self.time_limit:
                # Failed the speed run, create a new mission
                return False
        
        return False
    
    def get_progress(self):
        """Get current progress as a percentage"""
        if self.mission_type == "collect":
            return min(100, int((self.coins_collected / self.target_amount) * 100))
        elif self.mission_type == "avoid":
            return min(100, int((self.obstacles_avoided / self.target_amount) * 100))
        elif self.mission_type in ["survive", "perfect"]:
            return min(100, int((self.time_survived / self.target_amount) * 100))
        else:  # speed
            # For speed, progress is score progress with time decay
            score_progress = min(100, int((self.coins_collected / self.target_amount) * 100))
            time_remaining_pct = max(0, (self.time_limit - self.time_survived) / self.time_limit)
            # Progress bar shows score progress but reduced as time runs out
            return int(score_progress * time_remaining_pct)
    
    def get_progress_text(self):
        """Get progress text for display"""
        if self.mission_type == "collect":
            return f"{self.coins_collected}/{self.target_amount} coins"
        elif self.mission_type == "avoid":
            return f"{self.obstacles_avoided}/{self.target_amount} obstacles"
        elif self.mission_type == "survive":
            return f"{int(self.time_survived)}/{self.target_amount} seconds"
        elif self.mission_type == "perfect":
            return f"{int(self.time_survived)}/{self.target_amount} seconds perfect"
        else:  # speed
            return f"Score: {self.coins_collected}/{self.target_amount} (Time: {int(self.time_limit - self.time_survived)}s)"
        
            # Tile class
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, biome):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = tile_type
        self.biome = biome
        self.speed = 0
        self.set_appearance()
    
    def set_appearance(self):
        # Different appearances based on biome and tile type
        if self.type == "ground":
            if self.biome == FOREST:
                # Forest ground - grass with dirt
                self.image.fill((101, 67, 33))  # Dirt brown
                # Add grass on top
                pygame.draw.rect(self.image, FOREST_GREEN, (0, 0, TILE_SIZE, 8))
                # Add some texture details
                for _ in range(5):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(10, TILE_SIZE-3)
                    size = random.randint(1, 3)
                    pygame.draw.circle(self.image, (121, 85, 45), (x, y), size)
            
            elif self.biome == SEA:
                # Sea ground - sand
                self.image.fill((194, 178, 128))  # Sand color
                # Add some texture
                for _ in range(8):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    size = random.randint(1, 2)
                    pygame.draw.circle(self.image, (224, 205, 169), (x, y), size)
            
            elif self.biome == SNOW:
                # Snow ground
                self.image.fill(SNOW_WHITE)
                # Add some texture
                for _ in range(6):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    size = random.randint(1, 3)
                    pygame.draw.circle(self.image, (220, 220, 235), (x, y), size)
            
            elif self.biome == SKY:
                # Sky ground - clouds
                self.image.fill((200, 200, 255, 150))
                # Cloud texture
                for _ in range(5):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    size = random.randint(4, 8)
                    pygame.draw.circle(self.image, (255, 255, 255, 200), (x, y), size)
            
            else:  # SPACE
                # Space ground - asteroid surface
                self.image.fill((70, 70, 80))
                # Add crater details
                for _ in range(4):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    size = random.randint(2, 6)
                    pygame.draw.circle(self.image, (50, 50, 60), (x, y), size)
        
        elif self.type == "decoration":
            # Decorative tiles that appear on the ground
            if self.biome == FOREST:
                # Forest decoration - flowers or small plants
                self.image.fill((0, 0, 0, 0))  # Transparent background
                flower_color = random.choice([(255, 0, 0), (255, 255, 0), (255, 165, 0), (255, 192, 203)])
                pygame.draw.rect(self.image, FOREST_GREEN, (TILE_SIZE//2 - 1, TILE_SIZE//2, 2, TILE_SIZE//2))
                pygame.draw.circle(self.image, flower_color, (TILE_SIZE//2, TILE_SIZE//3), 4)
            
            elif self.biome == SEA:
                # Sea decoration - shells or small rocks
                self.image.fill((0, 0, 0, 0))  # Transparent
                shell_color = random.choice([(255, 222, 173), (255, 160, 122), (255, 182, 193)])
                # Draw a simple shell shape
                points = [(TILE_SIZE//2, TILE_SIZE//4), 
                         (TILE_SIZE//4, TILE_SIZE//2), 
                         (TILE_SIZE//2, 3*TILE_SIZE//4), 
                         (3*TILE_SIZE//4, TILE_SIZE//2)]
                pygame.draw.polygon(self.image, shell_color, points)
            
            elif self.biome == SNOW:
                # Snow decoration - small snowdrifts
                self.image.fill((0, 0, 0, 0))  # Transparent
                pygame.draw.ellipse(self.image, (255, 255, 255), 
                                   (TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//4))
            
            elif self.biome == SKY:
                # Sky decoration - small wisps
                self.image.fill((0, 0, 0, 0))  # Transparent
                pygame.draw.ellipse(self.image, (255, 255, 255, 100), 
                                   (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//4))
            
            else:  # SPACE
                # Space decoration - small asteroid
                self.image.fill((0, 0, 0, 0))  # Transparent
                pygame.draw.circle(self.image, (100, 100, 120), 
                                  (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//6)
    
    def set_speed(self, speed):
        self.speed = speed
    
    def update(self):
        self.rect.x -= self.speed
        # Return True if offscreen and should be removed
        return self.rect.right < 0
    
    # Power-Up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.power_type = random.choice(["shield", "jetpack", "magnet", "slowtime"])
        self.speed = speed
        
        # Define appearance based on power type
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        if self.power_type == "shield":
            pygame.draw.circle(self.image, BLUE, (12, 12), 12)
            pygame.draw.circle(self.image, WHITE, (12, 12), 6)
        elif self.power_type == "jetpack":
            self.image.fill(RED)
            pygame.draw.polygon(self.image, ORANGE, [(12, 5), (18, 20), (12, 15), (6, 20)])
        elif self.power_type == "magnet":
            self.image.fill(YELLOW)
            # Draw magnet shape
            pygame.draw.rect(self.image, RED, (5, 5, 15, 5))
            pygame.draw.rect(self.image, RED, (5, 15, 15, 5))
            pygame.draw.rect(self.image, RED, (5, 5, 5, 15))
        elif self.power_type == "slowtime":
            self.image.fill(GREEN)
            # Draw clock shape
            pygame.draw.circle(self.image, WHITE, (12, 12), 10, 1)
            pygame.draw.line(self.image, WHITE, (12, 12), (12, 6), 2)
            pygame.draw.line(self.image, WHITE, (12, 12), (18, 12), 2)
            
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(GROUND_LEVEL - 150, GROUND_LEVEL - 30)
        
        # Variables for movement and animation
        self.original_y = self.rect.y
        self.float_offset = 0
        self.float_speed = random.uniform(0.05, 0.15)
        
    def update(self):
        self.rect.x -= self.speed
        
        # Floating animation
        self.float_offset += self.float_speed
        self.rect.y = self.original_y + math.sin(self.float_offset) * 10
        
        if self.rect.right < 0:
            return True
        return False

# TileMap class to manage tiles
class TileMap:
    def __init__(self, biome):
        self.biome = biome
        self.ground_tiles = []
        self.decoration_tiles = []
        self.generate_initial_tiles()
    
    def generate_initial_tiles(self):
        # Create initial ground tiles
        for x in range(0, SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
            y = GROUND_LEVEL
            ground_tile = Tile(x, y, "ground", self.biome)
            self.ground_tiles.append(ground_tile)
            
            # Add some decoration tiles (less frequent)
            if random.random() < 0.3:  # 30% chance for decoration
                deco_tile = Tile(x, y - TILE_SIZE//2, "decoration", self.biome)
                self.decoration_tiles.append(deco_tile)
    
    def update(self, speed):
        # Update all tiles and remove offscreen ones
        for tile in list(self.ground_tiles):
            tile.set_speed(speed)
            if tile.update():
                self.ground_tiles.remove(tile)
        
        for tile in list(self.decoration_tiles):
            tile.set_speed(speed)
            if tile.update():
                self.decoration_tiles.remove(tile)
        
        # Add new tiles as needed
        if len(self.ground_tiles) > 0:
            # Get the rightmost tile position
            rightmost_x = max(tile.rect.right for tile in self.ground_tiles)
            
            # If we need more tiles to fill the screen
            if rightmost_x < SCREEN_WIDTH + TILE_SIZE:
                # Add a new ground tile
                ground_tile = Tile(rightmost_x, GROUND_LEVEL, "ground", self.biome)
                ground_tile.set_speed(speed)
                self.ground_tiles.append(ground_tile)
                
                # Maybe add decoration
                if random.random() < 0.3:
                    deco_tile = Tile(rightmost_x, GROUND_LEVEL - TILE_SIZE//2, "decoration", self.biome)
                    deco_tile.set_speed(speed)
                    self.decoration_tiles.append(deco_tile)
    
    def change_biome(self, new_biome):
        self.biome = new_biome
        # No need to immediately regenerate all tiles, let them phase out
        # as the player moves forward. New tiles will be the new biome.

class Path:
    def __init__(self, y_offset, difficulty, reward_multiplier):
        self.y_offset = y_offset  # Vertical offset from main path
        self.difficulty = difficulty  # 1-3, affects obstacle frequency
        self.reward_multiplier = reward_multiplier  # Multiplier for coin value

# Portal to enter side paths
class PathPortal(pygame.sprite.Sprite):
    def __init__(self, speed, is_entrance=True, destination_path=0):
        super().__init__()
        self.speed = speed
        self.is_entrance = is_entrance
        self.destination_path = destination_path  # Path index this portal leads to
        
        # Visual representation
        self.width = 40
        self.height = 70
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Portal color based on difficulty of path
        if destination_path == 0:  # Main path
            self.color = (100, 100, 255)  # Blue
        elif destination_path == 1:  # Easy side path
            self.color = (100, 255, 100)  # Green
        elif destination_path == 2:  # Medium side path
            self.color = (255, 255, 100)  # Yellow
        else:  # Hard side path
            self.color = (255, 100, 100)  # Red
        
        # Draw portal
        pygame.draw.ellipse(self.image, self.color, (0, 0, self.width, self.height))
        # Add swirl effect
        for i in range(3):
            radius = (i + 1) * 8
            pygame.draw.ellipse(self.image, (255, 255, 255, 150), 
                             (self.width//2 - radius//2, self.height//2 - radius//2, 
                              radius, radius), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        
        # Entrance portals are positioned on ground level
        # Exit portals are positioned based on their path
        if is_entrance:
            self.rect.y = GROUND_LEVEL - self.height
        else:
            # Will be positioned based on path's y_offset in game code
            self.rect.y = GROUND_LEVEL - self.height
        
        # Animation variables
        self.pulse_timer = 0
        self.scale_factor = 1.0

    def draw(self, screen):
        # Create a temporary scaled surface for pulsing effect
        scaled_width = int(self.width * self.scale_factor)
        scaled_height = int(self.height * self.scale_factor)
        scaled_image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
        
        # Center the scaled image on the original position
        scaled_rect = scaled_image.get_rect(center=self.rect.center)
        screen.blit(scaled_image, scaled_rect)
    


# Game class
class Game:
    def __init__(self):
        self.reset_game()
        self.current_mission = None
        self.completed_missions = 0
        self.failed_missions = 0
        self.mission_timer = 0
        self.difficulty_multiplier = 1.0
        self.player_hit_this_frame = False
        self.show_mission_complete_message = False
        self.message_timer = 0
        self.message_text = ""
        
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
        self.biome_change_score = 500
        self.ground_color = FOREST_GREEN
        self.sky_color = SKY_BLUE
        self.time_of_day = DAY
        self.time_cycle_counter = 0
        self.time_cycle_duration = 1000  # Frames until day/night change
        self.checkpoints = []
        self.checkpoint_timer = 0
        self.checkpoint_cooldown = 1000  # Spawn less frequently than obstacles
        self.current_checkpoint_biome = None
        self.has_checkpoint = False
        self.lives = 3  # Give player 3 lives
        # Initialize tilemap
        self.tilemap = TileMap(self.biome)
        # Initialize the sun/moon
        self.celestial_body = CelestialBody(self.time_of_day, self.biome)


        
    def run(self):
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle window resize events
                if event.type == pygame.VIDEORESIZE:
                    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL
                    if not is_fullscreen:
                        SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                        GROUND_LEVEL = SCREEN_HEIGHT - 100
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # Window control keys
                    if event.key == pygame.K_F11:  # F11 for fullscreen toggle
                        toggle_fullscreen()
                    
                    if event.key == pygame.K_F10:  # F10 for minimize
                        minimize_window()
                    
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
                    
                    if event.key == pygame.K_p:  # Press 'P' to toggle pause
                        if self.game_state == PLAYING:
                            self.game_state = PAUSED
                        elif self.game_state == PAUSED:
                            self.game_state = PLAYING
            
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
            elif self.game_state == PAUSED:
                self.draw_pause_screen()
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def update(self):

        self.coins_collected_this_frame = 0
        self.player_hit_this_frame = False

        # Check if player is alive
        if not self.player.is_alive:
            self.game_state = GAME_OVER
            return
            
        # Update player
        coins_collected = self.player.update(self.obstacles, self.coins)
        self.score += coins_collected
        self.coins_collected_this_frame = coins_collected

        
        # Increase speed gradually
        self.speed = min(15, 5 + (self.score / 500))

         
        # Update tilemap
        self.tilemap.update(self.speed)
        
        
        # Update day/night cycle
        self.time_cycle_counter += 1
        if self.time_cycle_counter >= self.time_cycle_duration:
            self.time_of_day = DAY if self.time_of_day == NIGHT else NIGHT
            self.time_cycle_counter = 0
            # Create new celestial body
            self.celestial_body = CelestialBody(self.time_of_day, self.biome)
            
            # Adjust sky color based on time of day
            self.update_sky_color()

        # Update checkpoints and check for collision
        for checkpoint in list(self.checkpoints):
            if checkpoint.update():
               self.checkpoints.remove(checkpoint)
            elif self.player.rect.colliderect(checkpoint.rect):
                # Checkpoint reached!
                self.current_checkpoint_biome = checkpoint.biome
                self.checkpoints.remove(checkpoint)
        
                # Visual effect for checkpoint (could add sound too)
                # Flash effect would go here
        
        # Check if we should spawn a checkpoint
        self.checkpoint_timer += 1
        if self.checkpoint_timer >= self.checkpoint_cooldown:
           self.spawn_checkpoint()
           self.checkpoint_timer = 0
        
        # Update celestial body
        self.celestial_body.update()
        
        # Update biome
        if self.score >= self.biome_change_score:
            self.biome = (self.biome + 1) % 5
            self.biome_change_score += 500

             # Update tilemap with new biome
            self.tilemap.change_biome(self.biome)


            # Reset checkpoint flag for new biome
            self.has_checkpoint = False
            
            # Create new celestial body for the new biome
            self.celestial_body = CelestialBody(self.time_of_day, self.biome)
            
            # Update environment colors
            self.update_environment_colors()

            # Update sky color
            self.update_sky_color()

            # Update mission 
            self.update_missions()
        
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
    
    def update_environment_colors(self):
        # Change ground and sky colors based on biome
        if self.biome == FOREST:
            self.ground_color = FOREST_GREEN
            self.update_sky_color()
        elif self.biome == SEA:
            self.ground_color = SEA_BLUE
            self.update_sky_color()
        elif self.biome == SNOW:
            self.ground_color = SNOW_WHITE
            self.update_sky_color()
        elif self.biome == SKY:
            self.ground_color = (135, 206, 250)  # Light sky blue
            self.update_sky_color()
        else:  # SPACE
            self.ground_color = (50, 50, 50)  # Dark gray
            self.sky_color = SPACE_BLACK  # Space is always dark
    
    def update_sky_color(self):
        # Adjust sky color based on time of day and biome
        if self.biome == SPACE:
            self.sky_color = SPACE_BLACK  # Space is always dark
            return
            
        if self.time_of_day == DAY:
            if self.biome == FOREST:
                self.sky_color = SKY_BLUE
            elif self.biome == SEA:
                self.sky_color = (173, 216, 230)  # Light blue
            elif self.biome == SNOW:
                self.sky_color = (200, 200, 255)  # Light blue-white
            elif self.biome == SKY:
                self.sky_color = (0, 191, 255)  # Deep sky blue
        else:  # NIGHT
            if self.biome == FOREST:
                self.sky_color = (25, 25, 112)  # Midnight blue
            elif self.biome == SEA:
                self.sky_color = (0, 0, 128)  # Navy
            elif self.biome == SNOW:
                self.sky_color = (70, 70, 100)  # Dark blue-gray
            elif self.biome == SKY:
                self.sky_color = (25, 25, 112)  # Midnight blue

    def spawn_checkpoint(self):
        # Only spawn checkpoint if we haven't already had one in this biome
        if not self.has_checkpoint:
           self.checkpoints.append(Checkpoint(self.biome, self.speed))
           self.has_checkpoint = True  # Mark that we've spawned a checkpoint for this biome

    def handle_player_death(self):
        if self.lives > 1:
            self.lives -= 1
        
            # Respawn player
            self.player = Player()
        
            # If player has reached a checkpoint, set the biome to match
            if self.current_checkpoint_biome is not None:
                # Reset to checkpoint biome
                self.biome = self.current_checkpoint_biome
                # Update tilemap biome
                self.tilemap.change_biome(self.biome)
                # Update celestial body
                self.celestial_body = CelestialBody(self.time_of_day, self.biome)
                # Update sky color
                self.update_sky_color()
        else:
            # No more lives, game over
            self.game_state = GAME_OVER
    
    def initialize_paths(self):
        # Define available paths
        self.paths = [
            Path(0, 1, 1.0),      # Main path: normal height, normal difficulty, normal rewards
            Path(-100, 1, 1.5),   # Upper path: higher up, easier, better rewards
            Path(50, 2, 2.0),     # Lower path: lower down, harder, best rewards
            Path(-200, 3, 3.0),   # Secret path: very high, very hard, amazing rewards
        ]
        self.current_path = 0  # Start on main path
    
         # Path-related variables
        self.path_portals = []
        self.portal_timer = 0
        self.portal_cooldown = FPS * 20  # Portal every 20 seconds
        self.path_duration = FPS * 15    # Paths last 15 seconds
        self.path_timer = 0              # Time spent on current side path
    
    def update_path_system(self):
        # Update existing portals
       for portal in list(self.path_portals):
           if portal.update():
               self.path_portals.remove(portal)
    
       # Check for portal collision
       for portal in list(self.path_portals):
           if self.player.rect.colliderect(portal.rect):
               if portal.is_entrance:
                   # Enter side path
                   self.current_path = portal.destination_path
                   self.path_timer = self.path_duration
                   # Apply visual transition based on path's y_offset
                   self.player.rect.y += self.paths[self.current_path].y_offset
                   # Remove all portals after using one
                   self.path_portals.clear()
               else:
                    # Return to main path
                    self.player.rect.y -= self.paths[self.current_path].y_offset
                    self.current_path = 0
                    self.path_portals.remove(portal)
    
        # If on a side path, count down timer
       if self.current_path != 0:
            self.path_timer -= 1
            if self.path_timer <= 0:
            # Time's up, create exit portal
              exit_portal = PathPortal(self.speed, False, 0)
            # Position exit portal
              exit_portal.rect.y = GROUND_LEVEL - exit_portal.height + self.paths[self.current_path].y_offset
              self.path_portals.append(exit_portal)
    
    # Spawn entrance portals on main path
       if self.current_path == 0:
            self.portal_timer += 1
            if self.portal_timer >= self.portal_cooldown:
            # Choose a random side path to create entrance for
               path_choice = random.randint(1, len(self.paths) - 1)
               portal = PathPortal(self.speed, True, path_choice)
               self.path_portals.append(portal)
               self.portal_timer = 0

    def draw_path_elements(self):
       # Draw path portals
       for portal in self.path_portals:
        portal.draw(screen)
        
    # If on a side path, draw timer
       if self.current_path != 0:
        time_left = self.path_timer // FPS
        path_text = font_small.render(f"Path Time: {time_left}s", True, WHITE)
        screen.blit(path_text, (SCREEN_WIDTH - path_text.get_width() - 10, 40))
        
        # Draw path info
        path_info = font_small.render(
            f"Path: {'Easy' if self.current_path == 1 else 'Medium' if self.current_path == 2 else 'Hard'} " +
            f"(Reward x{self.paths[self.current_path].reward_multiplier})", 
            True, WHITE)
        screen.blit(path_info, (SCREEN_WIDTH - path_info.get_width() - 10, 70))

    def draw_mission(self):
        """Draw mission info on screen"""
        if self.current_mission:
            # Change color based on mission difficulty
            mission_color = YELLOW
            if self.current_mission.mission_type in ["perfect", "speed"]:
               mission_color = RED  # Extreme missions are red
        
            # Draw mission box background
            mission_box = pygame.Surface((300, 80), pygame.SRCALPHA)
            mission_box.fill((0, 0, 0, 180))  # More opaque black
            screen.blit(mission_box, (SCREEN_WIDTH - 310, 50))
        
            # Draw mission title
            mission_title = font_medium.render("CURRENT MISSION", True, mission_color)
            screen.blit(mission_title, (SCREEN_WIDTH - 300, 60))
        
            # Draw mission description
            mission_desc = font_small.render(self.current_mission.description, True, WHITE)
            screen.blit(mission_desc, (SCREEN_WIDTH - 300, 90))
        
            # Draw progress bar
            progress = self.current_mission.get_progress()
            pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH - 300, 115, 280, 10))
        
            # Color-coded progress bar
            bar_color = GREEN
            if self.current_mission.mission_type == "perfect":
               bar_color = (0, 255, 255)  # Cyan for perfect missions
            elif self.current_mission.mission_type == "speed":
                # Gradient from green to red based on time remaining
                time_remaining = self.current_mission.time_limit - self.current_mission.time_survived
                if time_remaining < self.current_mission.time_limit * 0.3:
                    bar_color = RED  # Red when time is running out
                elif time_remaining < self.current_mission.time_limit * 0.6:
                    bar_color = ORANGE  # Orange when time is getting low
        
            pygame.draw.rect(screen, bar_color, (SCREEN_WIDTH - 300, 115, int(280 * progress / 100), 10))
        
            # Draw progress text
            progress_text = font_small.render(self.current_mission.get_progress_text(), True, WHITE)
            screen.blit(progress_text, (SCREEN_WIDTH - 150, 112))
        
        # Draw mission stats
        completed_text = font_small.render(f"Missions: {self.completed_missions} Completed | {self.failed_missions} Failed", True, WHITE)
        screen.blit(completed_text, (SCREEN_WIDTH - 310, 30))
    
        # Draw difficulty multiplier
        diff_text = font_small.render(
            f"Difficulty: x{self.difficulty_multiplier:.1f}", 
            True, YELLOW if self.difficulty_multiplier > 1.0 else WHITE
        )
        screen.blit(diff_text, (SCREEN_WIDTH - 150, 10))
    
        # Draw mission complete/failed message
        if hasattr(self, 'show_mission_complete_message') and self.show_mission_complete_message:
            if hasattr(self, 'message_timer'):
                self.message_timer -= 1
                if self.message_timer <= 0:
                   self.show_mission_complete_message = False
            
                # Make message pulse/fade
                alpha = min(255, self.message_timer * 2)
                scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 100)
            
                # Draw message
                message_font = pygame.font.SysFont("Arial", int(36 * scale))
                message_color = (255, 255, 0, alpha) if "COMPLETE" in self.message_text else (255, 0, 0, alpha)
                message_surf = message_font.render(self.message_text, True, message_color)
            
                # Center on screen
                message_rect = message_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
                screen.blit(message_surf, message_rect)
    
    def update_missions(self):
        """Update and manage missions"""
        # Create new mission if none exists
        if self.current_mission is None:
           # Increase difficulty multiplier based on completed missions
           # This makes missions progressively harder
            if self.completed_missions > 0:
              # Increase difficulty every 2 completed missions
              self.difficulty_multiplier = 1.0 + (self.completed_missions // 2) * 0.25
              # Cap at 3.0x difficulty
              self.difficulty_multiplier = min(3.0, self.difficulty_multiplier)
        
            self.current_mission = Mission(self.biome, self.difficulty_multiplier)
    
        # Count obstacles avoided (ones that moved off screen)
        obstacles_avoided = 0
        for obstacle in list(self.obstacles):
            if obstacle.rect.right < 0:
                obstacles_avoided += 1
    
        # Update current mission with expanded parameters
        mission_result = self.current_mission.update(
            self.biome, 
            delta_coins=self.coins_collected_this_frame,
            delta_obstacles=obstacles_avoided, 
            delta_time=1/FPS,
            player_hit=self.player_hit_this_frame,
            current_score=self.score
        )
    
        if mission_result is True:
            # Mission completed successfully!
            self.score += self.current_mission.reward
            self.completed_missions += 1
        
            # Create visual feedback (temporary text message)
            self.show_mission_complete_message = True
            self.message_timer = 120  # Display for 2 seconds
            self.message_text = f"MISSION COMPLETE! +{self.current_mission.reward} POINTS"
        
            self.current_mission = None  # Will create a new mission next frame
        
            # Optional: Play a sound or show an effect
            # if 'mission_complete' in sounds:
            #     sounds['mission_complete'].play()
    
        elif mission_result is False and self.current_mission and self.current_mission.mission_type in ["perfect", "speed"]:
            # Extreme mission failed - create new one
            self.failed_missions += 1
            self.current_mission = None
        
            # Create visual feedback for failed mission
            self.show_mission_complete_message = True
            self.message_timer = 120  # Display for 2 seconds
            self.message_text = "MISSION FAILED! TRY AGAIN!"

    
    def draw(self):
        # Draw background based on biome
        screen.fill(self.sky_color)
        
        # Draw sun/moon
        screen.blit(self.celestial_body.image, self.celestial_body.rect)
        
        # Draw background elements
        for bg_element in self.bg_elements:
            screen.blit(bg_element.image, bg_element.rect)
        

         # Draw ground tiles
        for tile in self.tilemap.ground_tiles:
            screen.blit(tile.image, tile.rect)

        # Draw decoration tiles
        for tile in self.tilemap.decoration_tiles:
            screen.blit(tile.image, tile.rect)
        
        
        # Draw obstacles
        for obstacle in self.obstacles:
            screen.blit(obstacle.image, obstacle.rect)
        
        # Draw coins
        for coin in self.coins:
            screen.blit(coin.image, coin.rect)

        # Draw checkpoints
        for checkpoint in self.checkpoints:
            screen.blit(checkpoint.image, checkpoint.rect)
    
        # Draw lives (add this near where you draw score)
        for i in range(self.lives):
            pygame.draw.rect(screen, ORANGE, (SCREEN_WIDTH - 30 - (i * 35), 15, 25, 25))
        
        # Draw player
        screen.blit(self.player.image, self.player.rect)
        self.draw_mission()


        # Draw score
        score_text = font_medium.render(f"Score: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw current biome
        biome_text = font_small.render(f"Biome: {biome_names[self.biome]}", True, WHITE)
        screen.blit(biome_text, (10, 40))
        
        # Draw time of day
        time_text = font_small.render(f"Time: {'Day' if self.time_of_day == DAY else 'Night'}", True, WHITE)
        screen.blit(time_text, (10, 70))

    def draw_menu(self):
        screen.fill(SPACE_BLACK)
        
        # Draw stars
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Draw moon or sun in menu
        menu_celestial = CelestialBody(random.choice([DAY, NIGHT]), SPACE)
        screen.blit(menu_celestial.image, (SCREEN_WIDTH - 100, 70))
        
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

        # Draw window controls info
        controls_text = font_small.render("F11: Toggle Fullscreen | F10: Minimize", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 500))
    
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
            "- The game gets faster as your score increases",
            "- Day and night cycle changes the sky color",
            "- Press P to pause or resume the game",
            "- Collect power-ups for special abilities:",
            "    Shield: Protects you from one obstacle",
            "    Jetpack: Allows you to fly for a short time",
            "    Magnet: Attracts nearby coins",
            "    Slow Time: Slows down obstacles temporarily",
            "- F11 toggles fullscreen mode",
            "- F10 minimizes the window",
            "- Survive as long as possible!",
            ""
        ]
        
        for i, line in enumerate(inst_lines):
            line_text = font_small.render(line, True, WHITE)
            screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, 100 + i * 20))
        
        # Draw return prompt
        return_text = font_medium.render("Press ENTER or BACKSPACE to return", True, RED)
        screen.blit(return_text, (SCREEN_WIDTH // 2 - return_text.get_width() // 2, 500))
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = font_large.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        # Draw final score
        score_text = font_medium.render(f"Final Score: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 230))
        
        # Draw restart prompt
        restart_text = font_medium.render("Press ENTER to Restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 300))
        
        # Draw menu prompt
        menu_text = font_medium.render("Press BACKSPACE for Menu", True, WHITE)
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 350))
        
        # Draw biome reached
        biome_text = font_small.render(f"Highest Biome Reached: {biome_names[self.biome]}", True, WHITE)
        screen.blit(biome_text, (SCREEN_WIDTH // 2 - biome_text.get_width() // 2, 420))

    def draw_pause_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw "Paused" text
        pause_text = font_large.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        # Draw resume instructions
        resume_text = font_medium.render("Press P to Resume", True, WHITE)
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

# Sound effects (optional, uncomment to enable)
'''
def load_sounds():
    jump_sound = pygame.mixer.Sound("jump.wav")
    coin_sound = pygame.mixer.Sound("coin.wav")
    death_sound = pygame.mixer.Sound("death.wav")
    biome_change_sound = pygame.mixer.Sound("biome_change.wav")
    
    return {
        "jump": jump_sound,
        "coin": coin_sound,
        "death": death_sound,
        "biome_change": biome_change_sound
    }

# Then add to Player.jump():
# sounds["jump"].play()

# And when collecting coins:
# sounds["coin"].play()

# And when changing biomes:
# sounds["biome_change"].play()

# And when player dies:
# sounds["death"].play()

# Add to your sounds dictionary
sounds["checkpoint"] = pygame.mixer.Sound("checkpoint.wav")

# Play when checkpoint is collected
sounds["checkpoint"].play()
'''

# Main function
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
