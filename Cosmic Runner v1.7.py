import pygame
import random
import math
import sys
import os
import time
from biome_music import play_biome_music, stop_music, set_volume
from volume_slider import VolumeSlider

# Initialize pygame and mixer
try:
    pygame.init()
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing pygame: {e}")
    sys.exit(1)

# Screen dimensions
_initial_display_info = pygame.display.Info()
# Define reference initial dimensions for scaling calculations
REF_SCREEN_WIDTH = _initial_display_info.current_w - 100
REF_SCREEN_HEIGHT = _initial_display_info.current_h - 100
REF_GROUND_MARGIN = 100 # The designed margin for the ground area

# Current, dynamic screen dimensions
SCREEN_WIDTH = REF_SCREEN_WIDTH
SCREEN_HEIGHT = REF_SCREEN_HEIGHT
# Ground is now fixed at the bottom of the window
GROUND_LEVEL = SCREEN_HEIGHT - REF_GROUND_MARGIN + 75 # Fixed
# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Cosmic Runner - Celestia")

# Track window state
is_fullscreen = False
is_minimized = False
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

# Audio state
is_muted = False

def toggle_mute():
    global is_muted
    is_muted = not is_muted
    if is_muted:
        pygame.mixer.music.set_volume(0)
        set_volume(0)
    else:
        # Restore volume from slider
        volume = volume_slider.get_volume()
        pygame.mixer.music.set_volume(volume)
        set_volume(volume)

# Font
font_small = pygame.font.SysFont("Arial", 20)
font_medium = pygame.font.SysFont("Arial", 30)
font_large = pygame.font.SysFont("Arial", 40)
font_huge = pygame.font.SysFont("Arial", 60, bold=True)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Biomes
PLATEAU = 0 
DARK_FOREST = 1
DESERT = 2
SEA = 3
SNOW = 4
VOLCANO =5
SKY = 6
SPACE = 7
biome_names = ["Plateau", "Dark Forest", "Desert", "Sea","Snow","Volcano", "Sky", "Space"]

# Time of day
DAY = 0
NIGHT = 1

# Tile size
TILE_SIZE = 32

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
image_path = os.path.join(current_dir, "assets", "images")
sound_path = os.path.join(current_dir, "assets", "sounds")

# Enhanced runner image with better animation frames
def create_runner_sprite(size=TILE_SIZE * 1.5):
    """Create animated runner sprite with multiple frames"""
    runner_frames = []
    colors = [(0, 150, 255), (0, 180, 255), (0, 120, 255)]
    
    for i in range(4):  # 4 animation frames
        frame = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Body
        body_color = colors[i % len(colors)]
        pygame.draw.ellipse(frame, body_color, (size//4, size//3, size//2, size//2))
        
        # Head
        pygame.draw.circle(frame, WHITE, (size//2, size//4), size//6)
        
        # Simple eyes
        eye_y = size//4 - 2
        pygame.draw.circle(frame, BLACK, (size//2 - 4, eye_y), 2)
        pygame.draw.circle(frame, BLACK, (size//2 + 4, eye_y), 2)
        
        # Running animation - legs
        leg_offset = math.sin(i * math.pi / 2) * 5
        pygame.draw.line(frame, body_color, 
                        (size//2 - 8, size//2 + size//4), 
                        (size//2 - 8 + leg_offset, size - 5), 3)
        pygame.draw.line(frame, body_color, 
                        (size//2 + 8, size//2 + size//4), 
                        (size//2 + 8 - leg_offset, size - 5), 3)
        
        # Arms
        arm_offset = math.sin(i * math.pi / 2 + math.pi) * 3
        pygame.draw.line(frame, body_color,
                        (size//4, size//2),
                        (size//4 - 5 + arm_offset, size//2 + 8), 2)
        pygame.draw.line(frame, body_color,
                        (3*size//4, size//2),
                        (3*size//4 + 5 - arm_offset, size//2 + 8), 2)
        
        runner_frames.append(frame)
    
    return runner_frames


# Load or create runner frames
try:
    runner_image_path = os.path.join(image_path, "runner.png")
    if os.path.exists(runner_image_path):
        base_image = pygame.image.load(runner_image_path)
        runner_frames = [pygame.transform.scale(base_image, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))]
        # Create additional frames for animation
        for i in range(3):
            frame = pygame.transform.scale(base_image, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))
            runner_frames.append(frame)
    else:
        runner_frames = create_runner_sprite()
except pygame.error:
    runner_frames = create_runner_sprite()

# Precomputed coin sprite for memory optimization
def create_coin_sprite():
    """Create reusable coin sprite"""
    coin = pygame.Surface((15, 15), pygame.SRCALPHA)
    pygame.draw.circle(coin, YELLOW, (7, 7), 7)
    pygame.draw.circle(coin, (255, 215, 0), (7, 7), 5)  # Inner gold
    return coin

precomputed_coin_sprite = create_coin_sprite()

# Load and set window icon with error handling
try:
    logo_image_path = os.path.join(image_path, "sapphire-logo.png")
    if os.path.exists(logo_image_path):
        window_icon = pygame.transform.scale(pygame.image.load(logo_image_path), (64, 64))
        pygame.display.set_icon(window_icon)
except (pygame.error, FileNotFoundError):
    pass  # Skip if logo doesn't exist

#lives and checkpoints
lives = 3
last_checkpoint_x = 150  # Default respawn X
last_checkpoint_biome = 0
biomes_with_checkpoint = set()

# Window controls function with resolution optimization
def toggle_fullscreen():
    global screen, is_fullscreen, windowed_size, SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL, volume_slider
    
    if is_fullscreen:
        # Return to windowed mode
        screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
        SCREEN_WIDTH, SCREEN_HEIGHT = windowed_size
        is_fullscreen = False
    else:
        # Save current window size before going fullscreen
        windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        # Switch to fullscreen with native resolution
        info = pygame.display.Info()
        SCREEN_WIDTH = info.current_w
        SCREEN_HEIGHT = info.current_h
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        is_fullscreen = True
    
    # Update ground level proportionally
    if REF_SCREEN_HEIGHT > 0:
        current_ground_margin = int(REF_GROUND_MARGIN * (SCREEN_HEIGHT / REF_SCREEN_HEIGHT))
    else: # Fallback
        current_ground_margin = REF_GROUND_MARGIN 
    GROUND_LEVEL = SCREEN_HEIGHT - current_ground_margin
    
    # Update volume slider position for new resolution
    volume_slider.rect.x = 50
    volume_slider.rect.y = SCREEN_HEIGHT - 150
    volume_slider.handle_rect.x = volume_slider.rect.x + volume_slider.width * volume_slider.volume - 10

def handle_window_resize(new_size):
    global SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL, windowed_size
    if not is_fullscreen:
        SCREEN_WIDTH, SCREEN_HEIGHT = new_size
        windowed_size = new_size
        
        # Update ground level proportionally
        if REF_SCREEN_HEIGHT > 0:
            current_ground_margin = int(REF_GROUND_MARGIN * (SCREEN_HEIGHT / REF_SCREEN_HEIGHT))
        else:
            current_ground_margin = REF_GROUND_MARGIN 
        GROUND_LEVEL = SCREEN_HEIGHT - current_ground_margin

# Enhanced Volume Slider
class EnhancedVolumeSlider:
    def __init__(self, x, y, width=200, height=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x + width * 0.5 - 10, y - 5, 20, height + 10)
        self.volume = 0.5
        self.dragging = False
        self.width = width
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) or self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                self.update_volume(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_volume(event.pos[0])
    
    def update_volume(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(relative_x, self.width))
        self.volume = relative_x / self.width
        self.handle_rect.centerx = self.rect.x + relative_x
        
        if not is_muted:
            pygame.mixer.music.set_volume(self.volume)
            set_volume(self.volume)
    
    def get_volume(self):
        return self.volume
    
    def draw(self, screen, font):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        filled_width = int(self.width * self.volume)
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        pygame.draw.rect(screen, (0, 255, 0), filled_rect)
        pygame.draw.rect(screen, WHITE, self.handle_rect)
        pygame.draw.rect(screen, BLACK, self.handle_rect, 2)
        volume_text = font.render(f"Volume: {int(self.volume * 100)}%", True, WHITE)
        screen.blit(volume_text, (self.rect.x, self.rect.y - 30))

# Initialize enhanced volume slider
volume_slider = EnhancedVolumeSlider(x=50, y=SCREEN_HEIGHT - 150, width=200)
set_volume(volume_slider.get_volume())

# Load title screen music with error handling
try:
    title_music = os.path.join(bgm_path, "Chills.mp3")
    if os.path.exists(title_music):
        pygame.mixer.music.load(title_music)
        pygame.mixer.music.play(-1, fade_ms=1000)
except (pygame.error, FileNotFoundError) as e:
    print(f"Error loading title screen music: {e}")
set_volume(volume_slider.get_volume())  # Apply current slider volume

# Sound effects system
def load_sounds():
    sounds = {}
    sound_files = {
        "jump": "jump.mp3",
        "coin": "coin.mp3",
        "death": "death.wav",
        "checkpoint": "checkpoint.wav",
        "shield": "shield.wav"
    }
    
    for sound_name, sound_file in sound_files.items():
        try:
            sound_path = os.path.join(current_dir, "assets", "sounds", sound_file)
            if os.path.exists(sound_path):
                sounds[sound_name] = pygame.mixer.Sound(sound_path)
            else:
                sounds[sound_name] = None
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sound {sound_file}: {e}")
            sounds[sound_name] = None
    
    return sounds

# Cache for texture generation to reduce memory allocation
class TextureCache:
    """Simple texture cache to avoid recreating surfaces repeatedly"""
    def __init__(self, max_size=50):
        self.cache = {}
        self.max_size = max_size
        self.access_count = 0
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest entry when cache is full
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value

scene_texture_cache = TextureCache(100)

# Enhanced Obstacle Spacing Algorithm
class ObstacleSpawner:
    def __init__(self, game_instance):
        self.game = game_instance
        self.last_obstacle_x = 0
        self.min_gap = 350  # Minimum gap between obstacles - INCREASED for better spacing
        self.max_gap = 700  # Maximum gap between obstacles - INCREASED for better spacing
        self.landing_spot_guarantee = 250  # Minimum safe landing distance
        self.difficulty_scaling = 1.0
        
    def should_spawn_obstacle(self):
        """Enhanced obstacle spawning algorithm with guaranteed landing spots"""
        if not self.game.obstacles:
            return True
            
        # Get the rightmost obstacle position
        rightmost_x = max([obs.rect.x for obs in self.game.obstacles])
        
        # Calculate distance from screen edge
        distance_from_edge = SCREEN_WIDTH - rightmost_x
        
        # Adjust gaps based on player speed and difficulty
        speed_factor = self.game.speed / 5.0  # Normalize based on initial speed
        difficulty_factor = (self.game.current_biome + 1) * 0.1
        
        # Dynamic gap calculation
        adjusted_min_gap = self.min_gap * (1.2 - difficulty_factor)
        adjusted_max_gap = self.max_gap * (1.1 - difficulty_factor * 0.5)
        
        # Ensure minimum landing spot
        if distance_from_edge >= adjusted_min_gap:
            # Add some randomness but guarantee safe passages
            chance = random.random()
            
            # Higher chance of spawning after longer gaps
            spawn_probability = max(0.1, min(0.8, distance_from_edge / adjusted_max_gap))
            
            # Guarantee landing spots periodically
            obstacles_in_sequence = len([obs for obs in self.game.obstacles if obs.rect.x > rightmost_x - 600])
            if obstacles_in_sequence >= 3:  # Force a gap after 3 consecutive obstacles
                spawn_probability *= 0.3
            
            return chance < spawn_probability
        
        return False
    
    def get_spawn_position(self):
        """Get optimal spawn position for new obstacle"""
        return SCREEN_WIDTH + random.randint(50, 150)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = runner_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.y = GROUND_LEVEL - self.rect.height
        self.jumping = False
        self.velocity_y = 0
        self.is_alive = True
        self.animation_frames = 8
        self.animation_timer = 0
        self.animation_cooldown = 5
        self.game = None  # Reference to game instance
        
        # Load sounds
        self.sounds = load_sounds()
        
        # Jump mechanics - More realistic
        self.jump_speed = -15 # Reduced initial jump velocity
        self.gravity = 0.8    # Reduced gravity for more realistic feel
        self.max_jump_height = 150  # Reduced maximum jump height
        self.initial_y = 0     # Store initial Y position for jump height tracking
        self.on_ground = True  # Track if player is on ground

        # Jetpack system
        self.has_jetpack = False
        self.jetpack_fuel = 0
        self.max_jetpack_fuel = 300
        self.jetpack_thrust = -0.5

    def update_animation(self):
        """Enhanced animation system"""
        if self.jumping:
            # Use jumping frame (frame 2)
            self.current_frame = 2
        else:
            # Running animation
            self.animation_timer += 1
            if self.animation_timer >= self.animation_cooldown:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.animation_timer = 0
        
        self.image = self.frames[self.current_frame]
    
    def lose_life(self):
        if self.game and self.game.active_powerups.get("shield", False):
            # Shield protects from losing life
            if self.sounds.get("shield"):
                self.sounds["shield"].play()
            return
            
        self.is_alive = False
        if self.game:
            self.game.lives -= 1
            
            # Play death sound
            if self.sounds.get("death"):
                self.sounds["death"].play()
                
            if self.game.lives <= 0:
                self.game.state = GAME_OVER
            else:
                # Reset player state for respawn
                self.is_alive = True
                self.jumping = False
                self.velocity_y = 0
                
                # Find the most recent checkpoint
                last_checkpoint = self.game.current_checkpoint
                
                if last_checkpoint:
                    # Reset player position to checkpoint
                    self.rect.x = last_checkpoint.rect.x + 100
                    self.rect.y = GROUND_LEVEL - self.rect.height
                else:
                    # No checkpoint found, return to start
                    self.rect.x = 150
                    self.rect.y = GROUND_LEVEL - self.rect.height
                
                # Enter brief respawn invincibility
                self.game.respawn_state = True
                self.game.respawn_timer = 60  # 1 second invincibility
    
    def jump(self):
        if self.on_ground and not self.jumping:
            self.velocity_y = self.jump_speed
            self.jumping = True
            self.on_ground = False
            self.initial_y = self.rect.y
            if self.sounds.get("jump"):
                self.sounds["jump"].play()
            
            # Track jump for missions - FIXED: ensure this is counted
            if self.game:
                self.game.jumps_this_frame += 1
                # Debug: Also track total jumps in a separate counter
                if not hasattr(self.game, 'total_jumps'):
                    self.game.total_jumps = 0
                self.game.total_jumps += 1

    def use_jetpack(self):
        if self.has_jetpack and self.jetpack_fuel > 0:
            self.velocity_y += self.jetpack_thrust
            self.jetpack_fuel -= 2
            if self.jetpack_fuel <= 0:
                self.has_jetpack = False


    def update(self, obstacles, coins):
         # Update animation
        self.update_animation()
        
        # Handle jetpack
        if self.has_jetpack and self.jetpack_fuel > 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.on_ground:
                self.use_jetpack()

        # Gravity
        if  not self.on_ground or self.jumping:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y
            
            # Check if landed
            if self.rect.y >= GROUND_LEVEL - self.rect.height:
                self.rect.y = GROUND_LEVEL - self.rect.height
                self.jumping = False
                self.velocity_y = 0
                self.on_ground = True

        else:
            self.rect.y = GROUND_LEVEL - self.rect.height
            self.velocity_y = 0

        # Skip collision during respawn invincibility
        if not (self.game and self.game.respawn_state):
            # Collision with obstacles
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.rect):
                    # Check if successfully jumping over
                    jumping_over = (self.rect.bottom < obstacle.rect.centery and 
                                  self.velocity_y > 0)
                    
                    if jumping_over:
                        # Successfully jumped over
                        if self.game:
                            self.game.obstacles_avoided_this_frame += 1
                        continue
                        
                    if self.game and self.game.active_powerups.get("shield", False):
                        # Shield blocks the hit
                        if self.sounds.get("shield"):
                            self.sounds["shield"].play()
                        if self.game:
                            self.game.obstacles_avoided_this_frame += 1
                        continue
                    
                    # Player was hit
                    if self.game:
                        self.game.player_hit_this_frame = True
                    self.lose_life()
                    return 0
        
        # Collect coins with magnet powerup
        coins_collected = 0
        magnet_radius = 100 if self.game and self.game.active_powerups.get("coin_magnet", False) else 0
        
        for coin in list(coins):
            # Calculate distance to coin
            dx = coin.rect.centerx - self.rect.centerx
            dy = coin.rect.centery - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Move coins towards player if magnet is active
            if magnet_radius > 0 and distance < magnet_radius:
                move_speed = 6
                if distance > 0:
                    coin.rect.x -= dx / distance * move_speed
                    coin.rect.y -= dy / distance * move_speed
            
            # Collect on collision
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                coins_collected += 1
                if self.sounds.get("coin"):
                    self.sounds["coin"].play()
        
        return coins_collected

# Enhanced Obstacle class with more realistic appearances
class Obstacle(pygame.sprite.Sprite):

    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed
        self.type = random.randint(0, 4)
        self.avoided_counted = False
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)  # Temporary surface
        self.rect = self.image.get_rect()  # Initialize rect first
        
        
        # Create obstacle based on biome
        if biome == PLATEAU:
            self.create_plateau_obstacle()
        elif biome == DARK_FOREST:
            self.create_dark_forest_obstacle()
        elif biome == DESERT:
            self.create_desert_obstacle()
        elif biome == SEA:
            self.create_sea_obstacle()
        elif biome == VOLCANO:
            self.create_volcano_obstacle()
        elif biome == SKY:
            self.create_sky_obstacle()
        else:  # SPACE - Final biome
            self.create_space_obstacle()
            
        self.rect.x = SCREEN_WIDTH

    def create_plateau_obstacle(self):
        if self.type == 0:  # Rock formation
            width, height = random.randint(40, 60), random.randint(50, 80)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 128, 117), (0, 10, width, height-10))
            for _ in range(8):
                x, y = random.randint(5, width-5), random.randint(15, height-5)
                pygame.draw.circle(self.image, (160, 150, 140), (x, y), random.randint(2, 4))
        elif self.type == 1:  # Lava geyser
            width, height = 25, random.randint(80, 120)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 69, 19), (5, height-20, width-10, 20))
            for i in range(height//10):
                y = height - 20 - i*10
                stream_width = max(3, width//2 - i)
                pygame.draw.rect(self.image, (255, 69, 0), (width//2 - stream_width//2, y, stream_width, 8))
        elif self.type == 2:  # Obsidian spike
            width, height = 20, random.randint(60, 90)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            points = [(width//2, 0), (0, height), (width, height)]
            pygame.draw.polygon(self.image, (40, 40, 60), points)
            highlight_points = [(width//2, 0), (width//4, height//2), (3*width//4, height//2)]
            pygame.draw.polygon(self.image, (80, 80, 100), highlight_points)
        else:  # Fire crystal
            size = 35
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(size//2, 0), (size, size//3), (3*size//4, size), (size//4, size), (0, size//3)]
            pygame.draw.polygon(self.image, (255, 100, 0), points)
            inner_points = [(size//2, size//6), (3*size//4, size//2), (size//4, size//2)]
            pygame.draw.polygon(self.image, (255, 200, 0), inner_points)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - self.image.get_height()

    def create_dark_forest_obstacle(self):
        if self.type == 0:  # Dead tree
            width, height = random.randint(30, 50), random.randint(80, 120)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (40, 20, 10), (width//2-5, height//2, 10, height//2))
            for i in range(3):
                branch_y = height//3 + i*15
                pygame.draw.line(self.image, (60, 30, 15), (width//2, branch_y), (5, branch_y-10), 3)
                pygame.draw.line(self.image, (60, 30, 15), (width//2, branch_y), (width-5, branch_y-10), 3)
        elif self.type == 1:  # Thorny bush
            width, height = random.randint(50, 70), random.randint(40, 60)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (20, 40, 20), (0, height//3, width, 2*height//3))
            for _ in range(15):
                x = random.randint(5, width-5)
                y = random.randint(height//2, height-5)
                pygame.draw.line(self.image, (139, 69, 19), (x, y), (x+random.randint(-8,8), y-10), 2)
        else:  # Dark mushroom
            width, height = 40, random.randint(50, 70)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 69, 19), (width//2-3, height//2, 6, height//2))
            pygame.draw.ellipse(self.image, (139, 0, 139), (0, 0, width, height//2))
            for _ in range(5):
                x = random.randint(5, width-5)
                y = random.randint(5, height//3)
                pygame.draw.circle(self.image, WHITE, (x, y), 2)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - self.image.get_height()

    def create_desert_obstacle(self):
        if self.type == 0:  # Cactus
            width, height = random.randint(25, 40), random.randint(60, 100)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (34, 139, 34), (width//2-8, 20, 16, height-20))
            if random.choice([True, False]):
                pygame.draw.rect(self.image, (34, 139, 34), (5, height//2-5, width//2, 10))
            if random.choice([True, False]):
                pygame.draw.rect(self.image, (34, 139, 34), (width//2, height//3, width//2-5, 10))
            for _ in range(12):
                x = random.randint(width//2-8, width//2+8)
                y = random.randint(25, height-5)
                pygame.draw.line(self.image, (255, 255, 255), (x, y), (x+3, y), 1)
        elif self.type == 1:  # Sand dune
            width, height = random.randint(60, 100), random.randint(30, 50)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            points = [(0, height)]
            for i in range(10):
                x = i * width // 9
                y = height - 10 - abs(math.sin(i * 0.8) * 20)
                points.append((x, int(y)))
            points.append((width, height))
            pygame.draw.polygon(self.image, (238, 203, 173), points)
        else:  # Rock formation
            width, height = random.randint(40, 60), random.randint(40, 70)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (160, 82, 45), (0, height//3, width, 2*height//3))
            pygame.draw.ellipse(self.image, (139, 69, 19), (width//4, 0, width//2, height//2))
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - self.image.get_height()

    def create_sea_obstacle(self):
        if self.type == 0:  # Coral reef
            width, height = random.randint(50, 80), random.randint(60, 100)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            colors = [(255, 127, 80), (255, 99, 71), (255, 160, 122)]
            for i in range(4):
                color = random.choice(colors)
                branch_width = random.randint(12, 20)
                branch_height = random.randint(20, 40)
                x = i * width // 4
                y = height - branch_height
                pygame.draw.ellipse(self.image, color, (x, y, branch_width, branch_height))
        elif self.type == 1:  # Giant kelp
            width, height = 30, random.randint(100, 150)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for strand in range(2):
                x_base = strand * 15 + 5
                for y in range(0, height, 8):
                    wave = math.sin((y + strand * 30) * 0.08) * 6
                    pygame.draw.circle(self.image, (46, 125, 50), (x_base + int(wave), y), 3)
        elif self.type == 2:  # Sea anemone
            width, height = random.randint(40, 60), random.randint(50, 80)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (138, 43, 226), (0, height//2, width, height//2))
            for i in range(8):
                angle = i * math.pi / 4
                tentacle_end_x = width//2 + math.cos(angle) * width//3
                tentacle_end_y = height//2 + math.sin(angle) * height//4
                pygame.draw.line(self.image, (75, 0, 130), 
                               (width//2, height//2), 
                               (int(tentacle_end_x), int(tentacle_end_y)), 3)
        else:  # Underwater rock
            width, height = random.randint(45, 70), random.randint(40, 65)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (105, 105, 105), (0, height//4, width, 3*height//4))
            for _ in range(6):
                x = random.randint(5, width-5)
                y = random.randint(height//3, height-5)
                pygame.draw.circle(self.image, (34, 139, 34), (x, y), random.randint(2, 5))
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - self.image.get_height()
        
    def create_snow_obstacle(self):
        if self.type == 0:  # Snowman
            self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
            # Snowman body (3 circles)
            pygame.draw.circle(self.image, (255, 255, 255), (20, 50), 15)  # Bottom
            pygame.draw.circle(self.image, (255, 255, 255), (20, 35), 12)  # Middle  
            pygame.draw.circle(self.image, (255, 255, 255), (20, 22), 8)   # Head
            # Face
            pygame.draw.circle(self.image, (0, 0, 0), (17, 20), 1)  # Left eye
            pygame.draw.circle(self.image, (0, 0, 0), (23, 20), 1)  # Right eye
            pygame.draw.circle(self.image, (255, 165, 0), (20, 23), 1)  # Nose
            self.rect = self.image.get_rect()
            self.rect.y = GROUND_LEVEL - 60
        elif self.type == 1:  # Ice spike
            height = random.randint(50, 80)
            self.image = pygame.Surface((20, height), pygame.SRCALPHA)
            # Create icicle shape
            points = [(10, 0), (0, height), (20, height)]
            pygame.draw.polygon(self.image, (173, 216, 230), points)
            # Add ice shine
            pygame.draw.polygon(self.image, (224, 255, 255), [(10, 0), (5, height//2), (15, height//2)], 2)
            self.rect = self.image.get_rect()
            self.rect.y = GROUND_LEVEL - height
        elif self.type == 2:  # Snow drift
            self.image = pygame.Surface((60, 30), pygame.SRCALPHA)
            # Create mounded snow shape
            points = [(0, 30), (15, 10), (30, 5), (45, 10), (60, 30)]
            pygame.draw.polygon(self.image, (255, 255, 255), points)
            pygame.draw.polygon(self.image, (240, 248, 255), [(5, 25), (15, 15), (25, 12), (35, 15), (50, 25)], 0)
            self.rect = self.image.get_rect()
            self.rect.y = GROUND_LEVEL - 30
        else:  # Frozen tree
            self.image = pygame.Surface((35, 70), pygame.SRCALPHA)
            # Brown trunk
            pygame.draw.rect(self.image, (101, 67, 33), (0, 0, 35, 70))
            # Add ice coating
            pygame.draw.rect(self.image, (173, 216, 230, 100), (0, 0, 35, 70))
            # Frozen branches
            for i in range(3):
                y_pos = 15 + i * 20
                pygame.draw.line(self.image, (173, 216, 230), (5, y_pos), (30, y_pos - 5), 3)
            self.rect = self.image.get_rect()
            self.rect.y = GROUND_LEVEL - 70

    def create_volcano_obstacle(self):
        if self.type == 0:  # Lava rock
            width, height = random.randint(50, 80), random.randint(60, 100)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (70, 35, 35), (0, height//3, width, 2*height//3))
            for _ in range(8):
                x = random.randint(5, width-5)
                y = random.randint(height//2, height-5)
                pygame.draw.circle(self.image, (255, 69, 0), (x, y), random.randint(2, 4))
        elif self.type == 1:  # Lava fountain
            width, height = 30, random.randint(100, 140)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 69, 19), (width//3, height-15, width//3, 15))
            for i in range(height//8):
                y = height - 15 - i*8
                fountain_width = max(2, width//2 - i//2)
                color = (255, 69 + i*2, 0) if i < 8 else (255, 255, 0)
                pygame.draw.rect(self.image, color, 
                               (width//2 - fountain_width//2, y, fountain_width, 6))
        elif self.type == 2:  # Volcanic crystal
            width, height = 35, random.randint(70, 100)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            points = [(width//2, 0), (width, height//2), (3*width//4, height), (width//4, height), (0, height//2)]
            pygame.draw.polygon(self.image, (255, 69, 0), points)
            inner_points = [(width//2, height//6), (2*width//3, height//3), (width//3, height//3)]
            pygame.draw.polygon(self.image, (255, 255, 0), inner_points)
        else:  # Magma pool
            width, height = random.randint(60, 90), 25
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 69, 0), (0, 0, width, height))
            pygame.draw.ellipse(self.image, (255, 255, 0), (width//4, height//4, width//2, height//2))
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - self.image.get_height()

    def create_sky_obstacle(self):
        if self.type == 0:  # Storm cloud
            width, height = random.randint(80, 120), random.randint(40, 60)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (105, 105, 105), (0, 0, width, height))
            pygame.draw.ellipse(self.image, (169, 169, 169), (10, 5, width-20, height-10))
            if random.random() < 0.3:
                pygame.draw.line(self.image, (255, 255, 0), 
                               (width//2, height), (width//2 + 10, height + 20), 3)
        elif self.type == 1:  # Wind turbine
            self.image = pygame.Surface((30, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (192, 192, 192), (13, 20, 4, 80))
            pygame.draw.line(self.image, (255, 255, 255), (15, 20), (5, 10), 3)
            pygame.draw.line(self.image, (255, 255, 255), (15, 20), (25, 10), 3)
            pygame.draw.line(self.image, (255, 255, 255), (15, 20), (15, 5), 3)
        elif self.type == 2:  # Hot air balloon
            self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255, 69, 0), (5, 0, 40, 50))
            pygame.draw.ellipse(self.image, (255, 140, 0), (10, 5, 30, 40))
            pygame.draw.rect(self.image, (139, 69, 19), (20, 50, 10, 10))
            pygame.draw.line(self.image, (0, 0, 0), (15, 45), (22, 50), 1)
            pygame.draw.line(self.image, (0, 0, 0), (35, 45), (28, 50), 1)
        else:  # Bird flock
            self.image = pygame.Surface((60, 30), pygame.SRCALPHA)
            for i, (x, y) in enumerate([(10, 15), (20, 10), (30, 5), (40, 10), (50, 15)]):
                pygame.draw.arc(self.image, (0, 0, 0), (x-3, y-2, 6, 4), 0, math.pi, 2)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - random.randint(80, 200)

    def create_space_obstacle(self):
        """Enhanced space obstacles for the final biome"""
        if self.type == 0:  # Large asteroid
            size = random.randint(50, 90)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            points = []
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                radius = size//2 + random.randint(-12, 12)
                x = size//2 + radius * math.cos(rad)
                y = size//2 + radius * math.sin(rad)
                points.append((x, y))
            pygame.draw.polygon(self.image, (105, 105, 105), points)
            # Add craters
            for _ in range(8):
                cx, cy = random.randint(8, size-8), random.randint(8, size-8)
                crater_size = random.randint(3, 8)
                pygame.draw.circle(self.image, (70, 70, 70), (cx, cy), crater_size)
                pygame.draw.circle(self.image, (50, 50, 50), (cx-1, cy-1), crater_size-2)
        elif self.type == 1:  # Space station debris
            self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (169, 169, 169), (0, 10, 60, 20))
            pygame.draw.rect(self.image, (255, 255, 255), (5, 13, 50, 14))
            pygame.draw.line(self.image, (255, 0, 0), (15, 10), (20, 30), 3)
            pygame.draw.line(self.image, (255, 0, 0), (35, 10), (40, 30), 3)
            # Sparking effect
            for _ in range(5):
                x = random.randint(10, 50)
                y = random.randint(8, 32)
                pygame.draw.circle(self.image, (255, 255, 0), (x, y), 1)
        elif self.type == 2:  # Alien mothership
            self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (128, 128, 128), (10, 20, 60, 25))
            pygame.draw.ellipse(self.image, (192, 192, 192), (20, 10, 40, 25))
            # Alien lights
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            for i, x in enumerate([15, 30, 45, 60]):
                color = colors[i % len(colors)]
                pygame.draw.circle(self.image, color, (x, 32), 4)
        else:  # Satellite wreckage
            self.image = pygame.Surface((55, 45), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (105, 105, 105), (20, 15, 15, 25))
            # Broken solar panels
            pygame.draw.rect(self.image, (0, 0, 139), (0, 17, 15, 21))
            pygame.draw.rect(self.image, (0, 0, 139), (40, 17, 15, 21))
            # Damaged antenna
            pygame.draw.line(self.image, (255, 255, 255), (27, 15), (35, 0), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (35, 0), 3)
            # Damage effects
            for _ in range(3):
                x = random.randint(15, 40)
                y = random.randint(12, 35)
                pygame.draw.line(self.image, (255, 100, 0), (x, y), (x+5, y+5), 1)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - random.randint(60, 180)
     
    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            return True
        return False

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Reuse precomputed coin sprite instead of creating new surface
        self.image = precomputed_coin_sprite.copy()
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
    def __init__(self, biome, speed, game=None):
        super().__init__()
        self.biome = biome
        self.speed = speed
        self.game = game
        self.activated = False
        
        # Define checkpoint size and appearance
        self.width = 30
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Different colors for each biome (Space is last)
        biome_colors = [
            (150, 111, 51),   # Plateau - brown
            (20, 60, 20),     # Dark Forest - dark green
            (238, 203, 173),  # Desert - sandy
            (0, 100, 200),    # Sea - blue
            (139, 69, 19),    # Volcano - orange/red
            (100, 200, 255),  # Sky - light blue
            (200, 100, 200)   # Space - purple (FINAL)
        ]
        
        self.color = biome_colors[biome] if biome < len(biome_colors) else (100, 100, 100)
        self.symbol = biome_names[biome][0] if biome < len(biome_names) else "?"
        
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, self.width, self.height), 2)
        pygame.draw.rect(self.image, (150, 75, 0), (0, 0, 5, self.height))
        
        font = pygame.font.SysFont("Arial", 18)
        symbol_text = font.render(self.symbol, True, (0, 0, 0))
        self.image.blit(symbol_text, (self.width//2 - symbol_text.get_width()//2, 
                                     self.height//2 - symbol_text.get_height()//2))
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = GROUND_LEVEL - self.height
        
        self.animation_counter = 0
        self.wave_amplitude = 1
        
    def update(self):
        self.rect.x -= self.speed
        
        # Update checkpoint animation
        self.animation_counter += 1
        if self.animation_counter >= 3:
            self.animation_counter = 0
            self.wave_amplitude = random.randint(2, 5)
        
        # Check if player has reached this checkpoint
        if self.game and self.rect.x < 200 and not self.activated:  # Player is near checkpoint
            self.game.current_checkpoint = self  # Update current checkpoint
            self.game.biome_checkpoints[self.biome] = self  # Store checkpoint for this biome
            self.game.has_checkpoint = True
            self.activated = True
            
            # Play checkpoint activation sound
            if hasattr(self.game, 'sounds') and 'checkpoint' in self.game.sounds and self.game.sounds['checkpoint']:
                self.game.sounds['checkpoint'].play()
        
        # Return True if off-screen
        if self.rect.right < 0:
            return True
        return False

# Enhanced Background elements for each biome with more realistic appearances
class BackgroundElement(pygame.sprite.Sprite):
    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed * 0.3  # Background moves slower for parallax effect
        
        if biome == PLATEAU:
            self.create_plateau_background()
        elif biome == DARK_FOREST:
            self.create_dark_forest_background()
        elif biome == DESERT:
            self.create_desert_background()
        elif biome == SEA:
            self.create_sea_background()
        elif biome == VOLCANO:
            self.create_volcano_background()
        elif biome == SKY:
            self.create_sky_background()
        else:  # SPACE - Enhanced final biome
            self.create_space_background()
        
        self.rect.x = SCREEN_WIDTH
    
    def create_space_background(self):
        """Enhanced space background for final biome"""
        choice = random.choice(['stars', 'nebula', 'planet', 'galaxy', 'comet'])
        
        if choice == 'stars':
            width, height = 150, 150
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for _ in range(random.randint(30, 80)):
                x = random.randint(0, width)
                y = random.randint(0, height)
                brightness = random.randint(150, 255)
                size = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]
                color = random.choice([(brightness, brightness, brightness),
                                     (brightness, brightness//2, brightness//2),
                                     (brightness//2, brightness//2, brightness),
                                     (brightness//2, brightness, brightness//2)])
                pygame.draw.circle(self.image, color, (x, y), size)
                
        elif choice == 'nebula':
            width, height = random.randint(200, 400), random.randint(150, 250)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            colors = [(128, 0, 128, 60), (0, 100, 200, 50), (200, 0, 100, 70), (100, 200, 50, 40)]
            for color in colors:
                for _ in range(15):
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    radius = random.randint(30, 80)
                    pygame.draw.circle(self.image, color[:3], (x, y), radius)
                    
        elif choice == 'planet':
            size = random.randint(100, 200)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            planet_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                           (255, 255, 100), (255, 100, 255), (100, 255, 255)]
            color = random.choice(planet_colors)
            pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
            
            # Add planet features
            for _ in range(5):
                feature_color = tuple(max(0, c - 80) for c in color)
                x = random.randint(size//6, 5*size//6)
                y = random.randint(size//6, 5*size//6)
                feature_size = random.randint(8, 25)
                pygame.draw.circle(self.image, feature_color, (x, y), feature_size)
                
            # Add rings for some planets
            if random.random() < 0.3:
                ring_color = (200, 200, 200, 100)
                pygame.draw.ellipse(self.image, ring_color[:3], 
                                  (size//6, size//2-5, 2*size//3, 10))
                                  
        elif choice == 'galaxy':
            width, height = random.randint(250, 350), random.randint(150, 200)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            center_x, center_y = width//2, height//2
            
            # Galaxy spiral
            for arm in range(2):
                for i in range(100):
                    angle = arm * math.pi + i * 0.1
                    radius = i * 0.8
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle) * 0.5
                    if 0 <= x < width and 0 <= y < height:
                        brightness = max(50, 200 - i * 2)
                        size = max(1, 3 - i//30)
                        pygame.draw.circle(self.image, (brightness, brightness//2, brightness//4), 
                                         (int(x), int(y)), size)
                                         
        else:  # comet
            width, height = 100, 30
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Comet head
            pygame.draw.circle(self.image, (200, 200, 255), (width-15, height//2), 8)
            pygame.draw.circle(self.image, (255, 255, 255), (width-15, height//2), 5)
            
            # Comet tail
            for i in range(width-20):
                tail_width = max(1, 8 - i//10)
                alpha = max(50, 255 - i*3)
                tail_color = (150, 150, 255) if i < 30 else (100, 100, 200)
                pygame.draw.circle(self.image, tail_color, (width-20-i, height//2), tail_width)
        
        self.rect = self.image.get_rect()
        if choice in ['stars', 'galaxy']:
            self.rect.y = random.randint(10, GROUND_LEVEL - 100)
        else:
            self.rect.y = random.randint(30, GROUND_LEVEL//2)

    def create_plateau_background(self):
        width, height = random.randint(200, 400), random.randint(100, 200)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        top_width = random.randint(width//2, 3*width//4)
        pygame.draw.rect(self.image, (160, 130, 100), (width//2 - top_width//2, 0, top_width, height//2))
        pygame.draw.polygon(self.image, (140, 110, 80), 
                           [(0, height), (width//2 - top_width//2, height//2), 
                            (width//2 + top_width//2, height//2), (width, height)])
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height

    def create_dark_forest_background(self):
        width, height = random.randint(80, 150), random.randint(200, 350)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(3):
            tree_x = i * width // 3
            tree_width = width // 4
            pygame.draw.rect(self.image, (20, 20, 20), (tree_x, height//2, tree_width, height//2))
            pygame.draw.ellipse(self.image, (10, 20, 10), (tree_x - tree_width, 0, tree_width*3, height//2))
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height

    def create_desert_background(self):
        choice = random.choice(['dunes', 'mountains'])
        if choice == 'dunes':
            width, height = random.randint(300, 500), random.randint(50, 120)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for layer in range(3):
                layer_height = height // (layer + 1)
                points = [(0, height)]
                for i in range(15):
                    x = i * width // 14
                    y = height - layer_height * (1 + 0.3 * math.sin(i * 0.8))
                    points.append((x, int(y)))
                points.append((width, height))
                dune_color = (238 - layer*20, 203 - layer*15, 173 - layer*10)
                pygame.draw.polygon(self.image, dune_color, points)
        else:
            width, height = random.randint(400, 600), random.randint(150, 300)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            points = [(0, height)]
            for i in range(8):
                x = i * width // 7
                y = random.randint(0, height//3)
                points.append((x, y))
            points.append((width, height))
            pygame.draw.polygon(self.image, (160, 82, 45), points)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height

    def create_sea_background(self):
        if random.choice([True, False]):
            width, height = 30, random.randint(200, 400)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for strand in range(3):
                x_offset = strand * 10
                for y in range(0, height, 10):
                    wave = math.sin((y + strand * 50) * 0.05) * 8
                    pygame.draw.circle(self.image, (46, 125, 50), (x_offset + int(wave), y), 4)
        else:
            width, height = random.randint(60, 100), random.randint(80, 150)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            colors = [(255, 127, 80), (255, 99, 71), (255, 160, 122)]
            for i in range(5):
                color = random.choice(colors)
                x = random.randint(0, width-20)
                y = random.randint(height//2, height-10)
                branch_height = random.randint(30, 60)
                pygame.draw.ellipse(self.image, color, (x, y-branch_height, 20, branch_height))
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height

    def create_volcano_background(self):
        width, height = random.randint(300, 500), random.randint(200, 400)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        points = [(0, height)]
        peak_x = width // 2
        points.append((peak_x, 0))
        for i in range(1, 5):
            x = peak_x + i * width // 8
            y = random.randint(height//4, height//2)
            points.append((x, y))
        points.append((width, height))
        pygame.draw.polygon(self.image, (80, 40, 40), points)
        
        pygame.draw.circle(self.image, (255, 100, 0), (peak_x, 0), 15)
        
        flow_points = [(peak_x, 0)]
        for i in range(10):
            x = peak_x + random.randint(-20, 20)
            y = i * height // 10
            flow_points.append((x, y))
        if len(flow_points) > 2:
            pygame.draw.lines(self.image, (255, 69, 0), False, flow_points, 5)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height

    def create_sky_background(self):
        choice = random.choice(['clouds', 'city'])
        if choice == 'clouds':
            width = random.randint(100, 200)
            height = random.randint(40, 80)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for i in range(3):
                cloud_color = (255, 255, 255, 120 - i*20)
                cloud_rect = (i*5, i*3, width - i*10, height - i*6)
                pygame.draw.ellipse(self.image, cloud_color[:3], cloud_rect)
            self.rect = self.image.get_rect()
            self.rect.y = random.randint(50, GROUND_LEVEL//2)
        else:
            width = random.randint(200, 400)
            height = random.randint(80, 150)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            building_width = width // 8
            for i in range(8):
                building_height = random.randint(height//3, height)
                x = i * building_width
                pygame.draw.rect(self.image, (50, 50, 80), (x, height - building_height, building_width-2, building_height))
                for row in range(building_height//15):
                    for col in range(building_width//8):
                        if random.random() < 0.3:
                            wx = x + col * 8 + 2
                            wy = height - building_height + row * 15 + 3
                            window_color = (255, 255, 0) if random.random() < 0.7 else (100, 200, 255)
                            pygame.draw.rect(screen, window_color, (wx, wy, 4, 6))
            self.rect = self.image.get_rect()
            self.rect.y = GROUND_LEVEL - height

    def create_snow_background(self):
        # Snow-covered mountains or pine trees
        if random.choice([True, False]):  # Mountain
            width, height = random.randint(200, 400), random.randint(150, 250)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Mountain silhouette
            points = [(0, height)]
            for i in range(5):
                x = i * width // 4
                y = random.randint(0, height//3)
                points.append((x, y))
            points.append((width, height))
            
            pygame.draw.polygon(self.image, (105, 105, 105), points)  # Mountain
            # Snow caps
            snow_points = points[1:-1]  # Remove base points
            snow_points.append((width, height//3))
            snow_points.append((0, height//3))
            pygame.draw.polygon(self.image, (255, 255, 255), snow_points)
        else:  # Pine tree
            width, height = 60, random.randint(120, 200)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Tree trunk
            pygame.draw.rect(self.image, (101, 67, 33), (width//2-5, height*2//3, 10, height//3))
            
            # Pine layers (triangle sections)
            for layer in range(3):
                y_offset = layer * height//4
                layer_height = height//3
                points = [(width//2, y_offset), (0, y_offset + layer_height), (width, y_offset + layer_height)]
                pygame.draw.polygon(self.image, (34, 100, 34), points)
                # Snow on branches
                pygame.draw.polygon(self.image, (255, 255, 255), 
                                  [(width//2, y_offset), (5, y_offset + layer_height), (width-5, y_offset + layer_height)], 3)
        
        self.rect = self.image.get_rect()
        self.rect.y = GROUND_LEVEL - height
    
    
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
        
        self.size = 30 if biome == SPACE else 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if time_of_day == DAY:
            if biome == SPACE:
                # Distant star in space
                pygame.draw.circle(self.image, (255, 255, 200), (self.size // 2, self.size // 2), self.size // 2)
                pygame.draw.circle(self.image, (255, 255, 255), (self.size // 2, self.size // 2), self.size // 3)
            else:
                pygame.draw.circle(self.image, SUN_COLOR, (self.size // 2, self.size // 2), self.size // 2)
                for i in range(8):
                    angle = math.radians(i * 45)
                    start_x = self.size // 2 + (self.size // 2) * math.cos(angle)
                    start_y = self.size // 2 + (self.size // 2) * math.sin(angle)
                    end_x = self.size // 2 + (self.size // 1.2) * math.cos(angle)
                    end_y = self.size // 2 + (self.size // 1.2) * math.sin(angle)
                    pygame.draw.line(self.image, SUN_COLOR, (start_x, start_y), (end_x, end_y), 3)
        else:
            if biome == SPACE:
                # Alien moon/planet
                colors = [(150, 150, 255), (255, 150, 150), (150, 255, 150)]
                moon_color = random.choice(colors)
                pygame.draw.circle(self.image, moon_color, (self.size // 2, self.size // 2), self.size // 2)
                for _ in range(3):
                    crater_size = random.randint(2, 5)
                    crater_x = random.randint(crater_size, self.size - crater_size)
                    crater_y = random.randint(crater_size, self.size - crater_size)
                    crater_color = tuple(max(0, c - 50) for c in moon_color)
                    pygame.draw.circle(self.image, crater_color, (crater_x, crater_y), crater_size)
            else:
                pygame.draw.circle(self.image, MOON_COLOR, (self.size // 2, self.size // 2), self.size // 2)
                for _ in range(5):
                    crater_size = random.randint(3, 7)
                    crater_x = random.randint(10, self.size - 10)
                    crater_y = random.randint(10, self.size - 10)
                    pygame.draw.circle(self.image, (180, 180, 180), (crater_x, crater_y), crater_size)
        
        self.rect = self.image.get_rect()
        
        if biome == SPACE:
            self.rect.x = random.randint(100, SCREEN_WIDTH - 100)
            self.rect.y = random.randint(50, GROUND_LEVEL - 100)
        else:
            self.rect.x = SCREEN_WIDTH - 100
            self.rect.y = 80
        
        self.angle = 0
        self.radius = 0
        self.center_x = self.rect.x
        self.center_y = self.rect.y
        
        if biome == SPACE:
            self.speed_x = random.uniform(-0.3, 0.3)
            self.speed_y = random.uniform(-0.3, 0.3)
        else:
            self.speed_x = -0.2
            self.speed_y = 0

    def update(self):
        if self.biome == SPACE:
            # In space, slight random movement
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            # Change direction occasionally
            if random.random() < 0.005:
                self.speed_x = random.uniform(-0.3, 0.3)
                self.speed_y = random.uniform(-0.3, 0.3)
                
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
        self.jumps_made = 0
        self.time_survived = 0
        self.perfect_run_broken = False
        
        # Apply difficulty scaling based on biome level and multiplier
        self.difficulty = (biome + 1) * difficulty_multiplier
        
        # Generate random mission based on biome
        # Higher biomes have chance for harder mission types
        if biome >= 3:  # Sky or Space biomes
            mission_types = ["collect", "avoid", "survive", "perfect", "jump"]
        else:
            mission_types = ["collect", "avoid", "survive", "jump"]
        self.mission_type = random.choice(mission_types)
        
        # Set mission parameters based on type and biome - harder with progression
        if self.mission_type == "collect":
            self.target_amount = int(random.randint(5, 12) * self.difficulty)
            self.description = f"Collect {self.target_amount} coins in {biome_names[biome]}"
        elif self.mission_type == "avoid":
            self.target_amount = int(random.randint(8, 15) * self.difficulty)
            self.description = f"Avoid {self.target_amount} obstacles in {biome_names[biome]}"
        elif self.mission_type == "jump":
            self.target_amount = int(random.randint(5, 12) * max(1, self.difficulty * 0.8))
            self.description = f"Make {self.target_amount} jumps in {biome_names[biome]}"
        elif self.mission_type == "survive":
            self.target_amount = int(random.randint(20, 45) * self.difficulty)
            self.description = f"Survive {self.target_amount} seconds in {biome_names[biome]}"
        elif self.mission_type == "perfect":
            # Perfect run - no hits for a certain distance/time
            self.target_amount = int(random.randint(15, 30) * self.difficulty)
            self.description = f"Perfect run for {self.target_amount} seconds in {biome_names[biome]}"
        
        # Set reward based on difficulty (biome level and target amount)
        base_reward = 75
        biome_multiplier = biome + 2
        target_factor = self.target_amount / 8
        
        # Higher rewards for harder mission types
        if self.mission_type == "perfect":
            base_reward = 200
        elif self.mission_type == "jump":
            base_reward = 100
        
        self.reward = int(base_reward * biome_multiplier * target_factor * difficulty_multiplier)
    
    def update(self, current_biome, delta_coins=0, delta_obstacles=0, delta_jumps=0, 
               delta_time=1/60, player_hit=False, current_score=0):
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
                
        elif self.mission_type == "jump":
            self.jumps_made += delta_jumps
            if self.jumps_made >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "survive":
            self.time_survived += delta_time
            if self.time_survived >= self.target_amount:
                self.completed = True
                return True
                
        elif self.mission_type == "perfect":
            # For perfect run: fail if player hit an obstacle
            if player_hit and not self.perfect_run_broken:
                self.perfect_run_broken = True
                return False  # Mission failed
            
            if not self.perfect_run_broken:
                self.time_survived += delta_time
                if self.time_survived >= self.target_amount:
                    self.completed = True
                    return True
        
        return False
    
    def get_progress(self):
        """Get current progress as a percentage"""
        if self.mission_type == "collect":
            return min(100, int((self.coins_collected / self.target_amount) * 100))
        elif self.mission_type == "avoid":
            return min(100, int((self.obstacles_avoided / self.target_amount) * 100))
        elif self.mission_type == "jump":
            return min(100, int((self.jumps_made / self.target_amount) * 100))
        elif self.mission_type in ["survive", "perfect"]:
            return min(100, int((self.time_survived / self.target_amount) * 100))
        return 0
    
    def get_progress_text(self):
        """Get progress text for display"""
        if self.mission_type == "collect":
            return f"{self.coins_collected}/{self.target_amount} coins"
        elif self.mission_type == "avoid":
            return f"{self.obstacles_avoided}/{self.target_amount} avoided"
        elif self.mission_type == "jump":
            return f"{self.jumps_made}/{self.target_amount} jumps"
        elif self.mission_type == "survive":
            return f"{int(self.time_survived)}/{self.target_amount} seconds"
        elif self.mission_type == "perfect":
            if self.perfect_run_broken:
                return "FAILED - Hit obstacle"
            return f"{int(self.time_survived)}/{self.target_amount} seconds perfect"
        return ""

# Decoration class - visual elements that don't cause collisions
class Decoration(pygame.sprite.Sprite):
    """Non-hazardous decorative elements that don't cause player death"""
    def __init__(self, x, y, decoration_type, biome):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = decoration_type
        self.biome = biome
        self.speed = 0
        self.is_decoration = True  # Flag to distinguish from obstacles
        self.set_appearance()
    
    def set_appearance(self):
        """Create decorative visual for this biome"""
        if self.biome == PLATEAU:
            # Small rocks and crystals
            rock_color = random.choice([(160, 140, 120), (180, 160, 140), (200, 180, 160)])
            size = random.randint(8, 20)
            pygame.draw.ellipse(self.image, rock_color, (TILE_SIZE//2-size//2, TILE_SIZE-size, size, size))
            
        elif self.biome == DARK_FOREST:
            # Small mushrooms and twigs
            if random.choice([True, False]):
                pygame.draw.circle(self.image, (139, 69, 19), (TILE_SIZE//2, TILE_SIZE-5), 2)
                pygame.draw.ellipse(self.image, (100, 0, 100), (TILE_SIZE//2-6, TILE_SIZE-15, 12, 8))
            else:
                pygame.draw.line(self.image, (101, 67, 33), (5, TILE_SIZE-2), (TILE_SIZE-5, TILE_SIZE-8), 2)
        
        elif self.biome == DESERT:
            # Desert plants
            pygame.draw.line(self.image, (34, 139, 34), (TILE_SIZE//2, TILE_SIZE), (TILE_SIZE//2, TILE_SIZE-15), 2)
            pygame.draw.circle(self.image, (34, 139, 34), (TILE_SIZE//2-5, TILE_SIZE-12), 3)
            pygame.draw.circle(self.image, (34, 139, 34), (TILE_SIZE//2+5, TILE_SIZE-12), 3)
        
        elif self.biome == SEA:
            # Seaweed
            for i in range(3):
                y_pos = TILE_SIZE - i * 6
                width = max(2, 8 - i)
                pygame.draw.rect(self.image, (46, 125, 50), (TILE_SIZE//2-width//2, y_pos-6, width, 6))
        
        elif self.biome == SNOW:
            # Snow formations
            pygame.draw.circle(self.image, (240, 248, 255), (TILE_SIZE//2, TILE_SIZE-10), random.randint(3, 7))
        
        elif self.biome == VOLCANO:
            # Volcanic rocks
            pygame.draw.circle(self.image, (139, 69, 19), (TILE_SIZE//2, TILE_SIZE-8), random.randint(4, 8))
        
        elif self.biome == SKY:
            # Floating particles
            pygame.draw.circle(self.image, (255, 255, 255), (TILE_SIZE//2, TILE_SIZE//2), random.randint(2, 4))
        
        else:  # SPACE
            # Decorative space crystals
            crystal_color = random.choice([(150, 100, 255), (100, 255, 150), (255, 100, 150)])
            pygame.draw.polygon(self.image, crystal_color, [(TILE_SIZE//2, TILE_SIZE//4), 
                                                             (TILE_SIZE//4, 3*TILE_SIZE//4), 
                                                             (3*TILE_SIZE//4, 3*TILE_SIZE//4)])
    
    def update(self, speed):
        """Move decoration with game speed"""
        self.rect.x -= speed
    
    def is_off_screen(self):
        """Check if decoration has left the screen"""
        return self.rect.x + self.rect.width < 0

# Fixed Tile class - removes black boxes
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, biome):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)  # Use SRCALPHA for transparency
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = tile_type
        self.biome = biome
        self.speed = 0
        self.is_decoration = False  # Not a decoration, this is ground
        self.set_appearance()
    
    def set_appearance(self):
        if self.type == "ground":
            if self.biome == PLATEAU:
                self.image.fill((139, 128, 117))
                # Add texture details
                for _ in range(8):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(2, TILE_SIZE-3)
                    pygame.draw.circle(self.image, (160, 150, 140), (x, y), random.randint(1, 3))
                # Add subtle border for better definition
                pygame.draw.rect(self.image, (120, 110, 100), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == DARK_FOREST:
                self.image.fill((40, 30, 20))
                # Add leaf litter texture
                for _ in range(6):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(2, TILE_SIZE-3)
                    pygame.draw.circle(self.image, (60, 50, 40), (x, y), random.randint(1, 2))
                # Add moss spots
                for _ in range(3):
                    x = random.randint(0, TILE_SIZE-5)
                    y = random.randint(0, TILE_SIZE-5)
                    pygame.draw.circle(self.image, (20, 60, 20), (x, y), random.randint(1, 3))
                pygame.draw.rect(self.image, (30, 20, 10), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == DESERT:
                self.image.fill((238, 203, 173))
                # Add sand grain texture
                for _ in range(12):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    brightness = random.randint(240, 255)
                    pygame.draw.circle(self.image, (brightness, brightness-30, brightness-60), (x, y), 1)
                # Add subtle dune pattern
                for i in range(0, TILE_SIZE, 4):
                    wave_y = int(2 + math.sin(i * 0.3) * 1)
                    pygame.draw.line(self.image, (228, 193, 163), (i, wave_y), (i+2, wave_y), 1)
                pygame.draw.rect(self.image, (218, 183, 153), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == SEA:
                self.image.fill((194, 178, 128))  # Sandy ocean floor
                # Add water effects
                for _ in range(10):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    pygame.draw.circle(self.image, (135, 206, 250, 120), (x, y), random.randint(1, 3))
                # Add seaweed spots
                for _ in range(4):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(2, TILE_SIZE-3)
                    pygame.draw.circle(self.image, (46, 125, 50), (x, y), random.randint(1, 2))
                pygame.draw.rect(self.image, (174, 158, 108), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == SNOW:
                self.image.fill(SNOW_WHITE)
                # Add snow texture with depth
                for _ in range(8):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    size = random.randint(1, 3)
                    brightness = random.randint(230, 255)
                    pygame.draw.circle(self.image, (brightness, brightness, brightness), (x, y), size)
                # Add subtle snow drifts
                for i in range(0, TILE_SIZE, 6):
                    drift_y = int(1 + math.sin(i * 0.4) * 1)
                    pygame.draw.line(self.image, (250, 250, 255), (i, drift_y), (i+3, drift_y), 1)
                pygame.draw.rect(self.image, (220, 220, 240), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == VOLCANO:
                self.image.fill((70, 35, 35))  # Dark volcanic rock
                # Add lava veins
                for _ in range(6):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(2, TILE_SIZE-3)
                    pygame.draw.circle(self.image, (255, 69, 0), (x, y), 1)
                # Add ember effects
                for _ in range(3):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    pygame.draw.circle(self.image, (255, 140, 0), (x, y), random.randint(1, 2))
                pygame.draw.rect(self.image, (50, 25, 25), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            elif self.biome == SKY:
                # Cloud platform
                self.image.fill((200, 220, 255))
                # Add cloud wisps
                for _ in range(8):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    pygame.draw.circle(self.image, (255, 255, 255), (x, y), random.randint(2, 5))
                # Add transparency effect
                for _ in range(4):
                    x = random.randint(5, TILE_SIZE-5)
                    y = random.randint(5, TILE_SIZE-5)
                    pygame.draw.circle(self.image, (220, 240, 255), (x, y), random.randint(3, 6))
                pygame.draw.rect(self.image, (180, 200, 235), (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
            else:  # SPACE - Final biome
                self.image.fill((30, 30, 50))  # Dark space metal
                # Add alien crystal formations
                for _ in range(5):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    crystal_color = random.choice([(150, 100, 255), (100, 255, 150), (255, 100, 150)])
                    pygame.draw.circle(self.image, crystal_color, (x, y), random.randint(1, 2))
                # Add energy veins
                for _ in range(3):
                    x = random.randint(2, TILE_SIZE-3)
                    y = random.randint(2, TILE_SIZE-3)
                    pygame.draw.circle(self.image, (100, 200, 255), (x, y), 1)
                # Add metallic border
                pygame.draw.rect(self.image, (80, 80, 120), (0, 0, TILE_SIZE, TILE_SIZE), 1)


    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0:
            return True
        return False

# PowerUp class for special abilities
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type, speed):
        super().__init__()
        self.type = powerup_type
        self.speed = speed
        # Realistic power-up durations (in seconds at 60 FPS)
        if powerup_type == "shield":
            self.duration = 240  # 4 seconds
        elif powerup_type == "speed":
            self.duration = 300  # 5 seconds  
        elif powerup_type == "coin_magnet":
            self.duration = 600  # 10 seconds
        elif powerup_type == "double_coins":
            self.duration = 420  # 7 seconds
        else:
            self.duration = 300  # Default 5 seconds
        
        # Create power-up appearance
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        
        if powerup_type == "shield":
            # Blue shield with sparkle effect
            pygame.draw.circle(self.image, (0, 100, 255), (12, 12), 12)
            pygame.draw.circle(self.image, (100, 150, 255), (12, 12), 8)
            # Shield pattern
            pygame.draw.circle(self.image, (200, 220, 255), (12, 12), 4)
        
        elif powerup_type == "speed":
            # Yellow/orange speed boost with motion lines
            pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 12)
            pygame.draw.circle(self.image, (255, 255, 0), (12, 12), 8)
            # Motion lines
            for i in range(3):
                y_offset = 8 + i * 3
                pygame.draw.line(self.image, (255, 255, 255), (2, y_offset), (8, y_offset), 2)
        
        elif powerup_type == "coin_magnet":
            # Purple magnet effect
            pygame.draw.circle(self.image, (128, 0, 128), (12, 12), 12)
            pygame.draw.circle(self.image, (200, 100, 200), (12, 12), 8)
            # Magnet symbol (simplified)
            pygame.draw.arc(self.image, (255, 255, 255), (6, 6, 12, 12), 0, math.pi, 2)
        
        elif powerup_type == "double_coins":
            # Green double coin effect
            pygame.draw.circle(self.image, (0, 200, 0), (12, 12), 12)
            pygame.draw.circle(self.image, (100, 255, 100), (12, 12), 8)
            # Two coin symbols
            pygame.draw.circle(self.image, (255, 215, 0), (8, 12), 3)
            pygame.draw.circle(self.image, (255, 215, 0), (16, 12), 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation
        self.float_offset = 0
        self.original_y = y
    
    def update(self):
        self.rect.x -= self.speed
        
        # Floating animation
        self.float_offset += 0.2
        self.rect.y = self.original_y + math.sin(self.float_offset) * 3
        
        if self.rect.right < 0:
            return True
        return False

# Game class - main game logic
class Game:
    def __init__(self):
        self.state = MENU
        self.score = 0
        self.total_coins = 0
        self.lives = 3
        self.distance = 0
        self.current_biome = PLATEAU
        self.time_of_day = DAY
        self.speed = 5
        self.obstacles = []
        self.coins = []
        self.background_elements = []
        self.tiles = []
        self.powerups = []
        self.celestial_body = None
        self.checkpoints = []
        self.decorations = []  # Separate list for decorative elements
        
        # Player
        self.player = Player()
        self.player.game = self

        # Enhanced obstacle spawning
        self.obstacle_spawner = ObstacleSpawner(self)
        
        # Mission system
        self.missions = []
        self.completed_missions = []
        self.mission_completion_timer = 0
        
        # Generate initial missions (one per biome)
        for biome in range(7):
            self.missions.append(Mission(biome, 1.0))
        
        # Checkpoint system
        self.current_checkpoint = None
        self.biome_checkpoints = {}
        self.has_checkpoint = False
        
        # Respawn system
        self.respawn_state = False
        self.respawn_timer = 0
        
        # Power-up system with realistic timers
        self.active_powerups = {}
        self.powerup_timers = {}
        
        # Animation and effects
        self.camera_shake = 0
        self.screen_flash = 0
        
        # Performance tracking
        self.frame_count = 0
        self.obstacles_avoided_this_frame = 0
        self.player_hit_this_frame = False
        self.coins_collected_this_frame = 0
        self.jumps_this_frame = 0
        
        # Biome transition
        self.biome_transition_timer = 0
        self.next_biome_distance = 1000  # Distance to next biome
        
        # Load sounds
        self.sounds = load_sounds()

        # Enhanced power-up spawning including jetpack
        if random.randint(1, 1000) == 1:
            powerup_types = ["shield", "speed", "coin_magnet", "double_coins", "jetpack"]
            # Higher chance of jetpack in space biome
            if self.current_biome == SPACE:
                weights = [0.2, 0.15, 0.2, 0.1, 0.35]
            else:
                weights = [0.25, 0.20, 0.25, 0.15, 0.15]
            powerup_type = random.choices(powerup_types, weights=weights)[0]
            
            y_pos = random.randint(GROUND_LEVEL - 200, GROUND_LEVEL - 100)
            powerup = PowerUp(SCREEN_WIDTH, y_pos, powerup_type, self.speed)
            self.powerups.append(powerup)
        
        # Spawn checkpoints
        checkpoint_distance = (self.current_biome + 1) * 400
        if (not self.has_checkpoint and self.distance >= checkpoint_distance and 
            self.current_biome not in self.biome_checkpoints):
            checkpoint = Checkpoint(self.current_biome, self.speed, self)
            self.checkpoints.append(checkpoint)
        
        # Spawn background elements
        spawn_chance = 150 if self.current_biome == SPACE else 200
        if random.randint(1, spawn_chance) == 1:
            bg_element = BackgroundElement(self.current_biome, self.speed)
            bg_element.rect.x = SCREEN_WIDTH + random.randint(0, 200)
            self.background_elements.append(bg_element)
        
        # Spawn ground tiles
        rightmost_tile = 0
        for tile in self.tiles:
            if tile.rect.right > rightmost_tile:
                rightmost_tile = tile.rect.right
        
        while rightmost_tile < SCREEN_WIDTH + 200:
            tile = Tile(rightmost_tile, GROUND_LEVEL, "ground", self.current_biome)
            self.tiles.append(tile)
            # Randomly spawn decorations on top of tiles
            if random.randint(1, 100) <= 20:  # 20% chance for decoration
                decoration = Decoration(rightmost_tile, GROUND_LEVEL - TILE_SIZE, "decoration", self.current_biome)
                self.decorations.append(decoration)
            rightmost_tile += TILE_SIZE

    def setup_biome(self):
        """Setup new biome with initial elements and environment"""
        # Create celestial body for the biome
        self.celestial_body = CelestialBody(self.time_of_day, self.current_biome)
        
        # Spawn initial background elements for biome
        for _ in range(3):
            bg_element = BackgroundElement(self.current_biome, self.speed)
            bg_element.rect.x = SCREEN_WIDTH + random.randint(0, 400)
            self.background_elements.append(bg_element)
        
        # Refill ground tiles for new biome
        for tile in list(self.tiles):
            if tile.rect.x > SCREEN_WIDTH:
                self.tiles.remove(tile)
        
        # Clear old decorations
        self.decorations = [d for d in self.decorations if d.rect.x <= SCREEN_WIDTH]
        
        rightmost_tile = SCREEN_WIDTH
        while rightmost_tile < SCREEN_WIDTH + 400:
            tile = Tile(rightmost_tile, GROUND_LEVEL, "ground", self.current_biome)
            self.tiles.append(tile)
            # Add decorative elements instead of decoration tiles
            if random.random() < 0.3:
                deco = Decoration(rightmost_tile, GROUND_LEVEL - TILE_SIZE, "decoration", self.current_biome)
                self.decorations.append(deco)
            rightmost_tile += TILE_SIZE
        
        # Initial checkpoint for new biome
        checkpoint_distance = (self.current_biome + 1) * 600
        if self.distance >= checkpoint_distance and self.current_biome not in self.biome_checkpoints:
            checkpoint = Checkpoint(self.current_biome, self.speed, self)
            self.checkpoints.append(checkpoint)

    def transition_biome(self):
        """Enhanced biome transition - Space is final with smooth transition"""
        # Pause spawning during transition for smooth experience
        self.biome_transition_timer = 180  # 3 seconds pause for smooth transition
        
        self.current_biome = (self.current_biome + 1) % 8  # Changed to % 8 to include Space biome
        
        # Toggle day/night cycle for each biome transition
        self.time_of_day = NIGHT if self.time_of_day == DAY else DAY
        
        self.next_biome_distance += 800
        self.has_checkpoint = False
        
        # Clear existing obstacles for smooth transition
        self.obstacles.clear()
        
        # CHANGE MUSIC FOR NEW BIOME with smooth fade
        play_biome_music(self.current_biome, fade_duration_ms=1500)
        
        self.setup_biome()
        self.screen_flash = 80  # Enhanced flash for better visual feedback
        self.camera_shake = 20
        
        # Play transition sound if available
        if hasattr(self, 'sounds') and self.sounds and 'checkpoint' in self.sounds:
            try:
                self.sounds['checkpoint'].play()
            except:
                pass
        
        # Special message when reaching space
        if self.current_biome == SPACE:
            self.screen_flash = 120  # Extended flash for final biome
            self.camera_shake = 30
      
    def generate_ground_tiles(self):
        tile_x = 0
        while tile_x < SCREEN_WIDTH + 100:
            # Ground tiles with proper transparency
            tile = Tile(tile_x, GROUND_LEVEL, "ground", self.current_biome)
            self.tiles.append(tile)
            
            if random.random() < 0.3:
                deco_tile = Tile(tile_x, GROUND_LEVEL - TILE_SIZE, "decoration", self.current_biome)
                self.tiles.append(deco_tile)
            
            tile_x += TILE_SIZE
        
    def update(self):
        """Main game update loop"""
        if self.state != PLAYING:
            return
        
        # Reset frame tracking
        self.obstacles_avoided_this_frame = 0
        self.player_hit_this_frame = False
        self.coins_collected_this_frame = 0
        self.jumps_this_frame = 0
        
        # Handle respawn invincibility
        if self.respawn_state:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn_state = False
        
        # Update camera shake
        if self.camera_shake > 0:
            self.camera_shake -= 1
        
        # Update screen flash
        if self.screen_flash > 0:
            self.screen_flash -= 2
        
        # Increase speed gradually - more realistic progression
        if self.frame_count % 900 == 0:  # Every 15 seconds
            self.speed += 0.1
        
        # Update player
        coins_collected = self.player.update(self.obstacles, self.coins)
        self.coins_collected_this_frame = coins_collected
        self.score += coins_collected * 10
        self.total_coins += coins_collected
        
        # If player collected coins with double_coins powerup
        if coins_collected > 0 and self.active_powerups.get("double_coins", False):
            self.score += coins_collected * 10  # Double the points
            self.total_coins += coins_collected  # Double the coins
        
        # Update obstacles
        for obstacle in list(self.obstacles):
            if obstacle.update():
                self.obstacles.remove(obstacle)
            else:
                # Check if player passed obstacle (for mission tracking)
                if obstacle.rect.right < self.player.rect.left and not obstacle.avoided_counted:
                    obstacle.avoided_counted = True
                    self.obstacles_avoided_this_frame += 1
        
        # Update coins
        for coin in list(self.coins):
            if coin.update():
                self.coins.remove(coin)
        
        # Update power-ups
        for powerup in list(self.powerups):
            if powerup.update():
                self.powerups.remove(powerup)
            elif self.player.rect.colliderect(powerup.rect):
                # Activate power-up
                self.activate_powerup(powerup.type, powerup.duration)
                self.powerups.remove(powerup)
        
        # Update active power-ups with realistic timers
        for powerup_type, timer in list(self.powerup_timers.items()):
            self.powerup_timers[powerup_type] = timer - 1
            if timer <= 0:
                self.deactivate_powerup(powerup_type)
        
        # Update background elements
        for bg_element in list(self.background_elements):
            if bg_element.update():
                self.background_elements.remove(bg_element)
        
        # Update tiles
        for tile in list(self.tiles):
            if tile.update(self.speed):
                self.tiles.remove(tile)
        
        # Update decorations (no collision checking - they're purely visual)
        for decoration in list(self.decorations):
            decoration.update(self.speed)
            if decoration.is_off_screen():
                self.decorations.remove(decoration)
        
        # Update celestial body
        if self.celestial_body:
            self.celestial_body.update()
        
        # Update checkpoints
        for checkpoint in list(self.checkpoints):
            if checkpoint.update():
                self.checkpoints.remove(checkpoint)
        
        # Spawn new elements
        self.spawn_elements()
        
        # Update distance and biome progression
        self.distance += self.speed * 0.1
        
        # Update biome transition timer
        if self.biome_transition_timer > 0:
            self.biome_transition_timer -= 1
            # Reduce speed during transition for smooth experience
            current_speed_multiplier = 0.7 + (self.biome_transition_timer / 180 * 0.3)
            display_speed = self.speed * current_speed_multiplier
        
        # Check for biome transition
        if self.distance >= self.next_biome_distance:
            self.transition_biome()
        
        # Update missions
        self.update_missions()
        
        # Update frame counter
        self.frame_count += 1
    
    def activate_powerup(self, powerup_type, duration):
        """Activate a power-up with its specific duration"""
        self.active_powerups[powerup_type] = True
        self.powerup_timers[powerup_type] = duration
        
        if powerup_type == "shield":
            self.camera_shake = 10
        elif powerup_type == "speed":
            self.speed += 2  # Reduced speed boost for more realistic feel
            self.screen_flash = 15
        elif powerup_type == "jetpack":
            self.player.has_jetpack = True
            self.player.jetpack_fuel = self.player.max_jetpack_fuel
            self.screen_flash = 10
        elif powerup_type == "coin_magnet":
            pass  # Passive effect
        elif powerup_type == "double_coins":
            pass  # Passive effect
        
        # Safe sound playing
        if hasattr(self, 'sounds') and self.sounds:
            if 'shield' in self.sounds and self.sounds['shield']:
                self.sounds['shield'].play()

    def deactivate_powerup(self, powerup_type):
        """Deactivate a power-up"""
        if powerup_type in self.active_powerups:
            del self.active_powerups[powerup_type]
        
        if powerup_type in self.powerup_timers:
            del self.powerup_timers[powerup_type]
        
        if powerup_type == "speed":
            self.speed = max(5, self.speed - 2)  # Remove speed boost
        elif powerup_type == "jetpack":
            self.player.has_jetpack = False
            self.player.jetpack_fuel = 0

    def spawn_elements(self):
        """Spawn obstacles, coins, power-ups, etc. - Optimized with reduced random calls"""
        # Don't spawn obstacles during biome transition for smooth gameplay
        if len(self.obstacles) == 0:
            # First obstacle - spawn far enough away
            if random.randint(1, 60) == 1:
                obstacle = Obstacle(self.current_biome, self.speed)
                obstacle.rect.x = SCREEN_WIDTH + 200  # Start further away
                self.obstacles.append(obstacle)
        else:
            # Check distance from last obstacle
            rightmost_obstacle = max(self.obstacles, key=lambda o: o.rect.x)
            distance_from_last = SCREEN_WIDTH - rightmost_obstacle.rect.x
            
            # Guaranteed minimum gap based on player jump capability
            min_gap = 250 + (self.speed * 10)  # Scales with speed
            max_gap = 450 + (self.speed * 15)
            
            if distance_from_last >= min_gap:
                # Only spawn with some probability to ensure gaps
                spawn_chance = min(80, 40 + int(distance_from_last / 20))
                if random.randint(1, spawn_chance) == 1:
                    obstacle = Obstacle(self.current_biome, self.speed)
                    obstacle.rect.x = SCREEN_WIDTH + random.randint(50, 150)
                    self.obstacles.append(obstacle)
            
            # Spawn coins - balanced frequency
            if random.randint(1, 80) == 1:
                coin = Coin(self.speed)
                self.coins.append(coin)
            
            # Power-ups including jetpack with better spawn rate
            if random.randint(1, 600) == 1:  # More frequent power-up spawns
                powerup_types = ["shield", "speed", "coin_magnet", "double_coins", "jetpack"]
                # Higher chance of jetpack in later biomes
                if self.current_biome >= 4:
                    weights = [0.2, 0.15, 0.2, 0.1, 0.35]
                else:
                    weights = [0.25, 0.20, 0.25, 0.15, 0.15]
                powerup_type = random.choices(powerup_types, weights=weights)[0]
                
                y_pos = random.randint(GROUND_LEVEL - 200, GROUND_LEVEL - 80)
                powerup = PowerUp(SCREEN_WIDTH, y_pos, powerup_type, self.speed)
                self.powerups.append(powerup)
        
        # Checkpoint spawning
        checkpoint_distance = (self.current_biome + 1) * 500
        if (not self.has_checkpoint and 
            self.distance >= checkpoint_distance and 
            self.current_biome not in self.biome_checkpoints):
            checkpoint = Checkpoint(self.current_biome, self.speed, self)
            self.checkpoints.append(checkpoint)
            self.has_checkpoint = True  # Mark as spawned
        
        # Spawn background elements - reduced spawn check frequency
        if random.randint(1, 150) == 1:
            bg_element = BackgroundElement(self.current_biome, self.speed)
            bg_element.rect.x = SCREEN_WIDTH + random.randint(0, 200)
            self.background_elements.append(bg_element)
        
        # Spawn ground tiles to fill gaps - optimized
        rightmost_tile = 0
        for tile in self.tiles:
            if tile.rect.right > rightmost_tile:
                rightmost_tile = tile.rect.right
        
        # Only spawn tiles if there's a gap
        if rightmost_tile < SCREEN_WIDTH + 200:
            while rightmost_tile < SCREEN_WIDTH + 200:
                tile = Tile(rightmost_tile, GROUND_LEVEL, "ground", self.current_biome)
                self.tiles.append(tile)
                
                # Spawn decorative elements separately (20% chance)
                if random.random() < 0.2:
                    deco = Decoration(rightmost_tile, GROUND_LEVEL - TILE_SIZE, "decoration", self.current_biome)
                    self.decorations.append(deco)
                
                rightmost_tile += TILE_SIZE
    
    def update_missions(self):
        """Update mission progress"""
        for mission in list(self.missions):
            if not mission.completed:
                # Check mission progress
                completed = mission.update(
                    self.current_biome,
                    self.coins_collected_this_frame,
                    self.obstacles_avoided_this_frame,
                    self.jumps_this_frame,
                    1/60,  # Delta time
                    self.player_hit_this_frame,
                    self.score
                )
                
                if completed:
                    # Mission completed!
                    self.completed_missions.append(mission)
                    self.total_coins += mission.reward
                    self.score += mission.reward * 5
                    self.missions.remove(mission)
                    
                    # Generate new mission for this biome
                    difficulty = 1.0 + (len(self.completed_missions) * 0.2)  # Increasing difficulty
                    new_mission = Mission(mission.biome, difficulty)
                    self.missions.append(new_mission)
                    
                    self.mission_completion_timer = 180  # Show completion message for 3 seconds
    
    def jump_input(self):
        """Handle jump input"""
        if self.player.on_ground:  # Only allow jumping when on ground
            self.player.jump()
    
    def reset_game(self):
        """Reset game state"""
        self.state = PLAYING
        self.score = 0
        self.lives = 3
        self.distance = 0
        self.current_biome = PLATEAU
        self.time_of_day = DAY
        self.speed = 5
        self.frame_count = 0
        
        # Clear all game objects
        self.obstacles.clear()
        self.coins.clear()
        self.background_elements.clear()
        self.tiles.clear()
        self.powerups.clear()
        self.checkpoints.clear()
        self.decorations.clear()
        
        # Reset player
        self.player = Player()
        self.player.game = self
        self.player.rect.x = 150
        self.player.rect.y = GROUND_LEVEL - self.player.rect.height

        # Reset obstacle spawner
        self.obstacle_spawner = ObstacleSpawner(self)
        
        # START BIOME MUSIC for Plateau
        play_biome_music(self.current_biome, fade_duration_ms=1000)
        
        # Reset mission system
        self.missions.clear()
        self.completed_missions.clear()
        for biome in range(5):
            self.missions.append(Mission(biome, 1.0))
        
        # Reset checkpoint system
        self.current_checkpoint = None
        self.biome_checkpoints.clear()
        self.has_checkpoint = False
        
        # Reset power-ups
        self.active_powerups.clear()
        self.powerup_timers.clear()
        
        # Reset biome
        self.next_biome_distance = 1000
    
    def get_background_color(self):
        """Enhanced background colors - Space has special deep space color"""
        day_colors = [
            (135, 206, 235),  # Plateau - sky blue
            (50, 50, 70),     # Dark Forest - dark
            (255, 218, 185),  # Desert - sandy
            (0, 105, 148),    # Sea - sea blue
            (139, 69, 19),    # Volcano - brown/orange
            (135, 206, 250),  # Sky - light blue
            (5, 5, 30)        # Space - deep space (FINAL)
        ]
        
        night_colors = [
            (25, 25, 60),     # Plateau night
            (10, 10, 20),     # Dark Forest night
            (139, 115, 85),   # Desert night
            (0, 50, 100),     # Sea night
            (80, 40, 40),     # Volcano night
            (50, 50, 100),    # Sky night
            (2, 2, 15)        # Space night - even darker
        ]
        
        colors = day_colors if self.time_of_day == DAY else night_colors
        return colors[self.current_biome] if self.current_biome < len(colors) else (50, 50, 50)
    
    
    def draw(self, screen):
        """Draw all game elements"""
        # Fill background
        bg_color = self.get_background_color()
        screen.fill(bg_color)
        
        # Apply camera shake
        shake_x = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
        shake_y = random.randint(-self.camera_shake, self.camera_shake) if self.camera_shake > 0 else 0
        
        # Draw background elements (with shake)
        for bg_element in self.background_elements:
            screen.blit(bg_element.image, (bg_element.rect.x + shake_x, bg_element.rect.y + shake_y))
        
        # Draw celestial body
        if self.celestial_body:
            screen.blit(self.celestial_body.image, (self.celestial_body.rect.x + shake_x, self.celestial_body.rect.y + shake_y))
        
        # Draw tiles
        for tile in self.tiles:
            screen.blit(tile.image, (tile.rect.x + shake_x, tile.rect.y + shake_y))
        
        # Draw decorations (visual-only, no collision)
        for decoration in self.decorations:
            screen.blit(decoration.image, (decoration.rect.x + shake_x, decoration.rect.y + shake_y))
        
        # Draw coins
        for coin in self.coins:
            screen.blit(coin.image, (coin.rect.x + shake_x, coin.rect.y + shake_y))
        
        # Draw power-ups
        for powerup in self.powerups:
            screen.blit(powerup.image, (powerup.rect.x + shake_x, powerup.rect.y + shake_y))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            screen.blit(obstacle.image, (obstacle.rect.x + shake_x, obstacle.rect.y + shake_y))
        
        # Draw checkpoints
        for checkpoint in self.checkpoints:
            screen.blit(checkpoint.image, (checkpoint.rect.x + shake_x, checkpoint.rect.y + shake_y))
        
        # Draw player (with respawn flashing)
        if self.respawn_state:
            if (self.respawn_timer // 5) % 2:  # Flash every 5 frames
                screen.blit(self.player.image, (self.player.rect.x + shake_x, self.player.rect.y + shake_y))
        else:
            screen.blit(self.player.image, (self.player.rect.x + shake_x, self.player.rect.y + shake_y))

        # Draw jetpack effects
        if self.player.has_jetpack and self.player.jetpack_fuel > 0:
            flame_x = self.player.rect.centerx + shake_x
            flame_y = self.player.rect.bottom + shake_y
            for i in range(4):
                flame_size = random.randint(4, 10)
                flame_offset_x = random.randint(-6, 6)
                flame_color = (255, 100, 0) if i % 2 else (255, 255, 0)
                pygame.draw.circle(screen, flame_color, (flame_x + flame_offset_x, flame_y + i*4), flame_size)
        
        # Draw UI elements
        self.draw_ui(screen)
        
        # Apply screen flash
        if self.screen_flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            if self.current_biome == SPACE:
                flash_surface.fill((100, 100, 255))  # Blue flash for space
            else:
                flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(self.screen_flash * 2)
            screen.blit(flash_surface, (0, 0))
    
    def draw_ui(self, screen):
        """Draw UI elements - Fixed powerup timer positioning"""
        # Score and basic stats
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font_medium.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        distance_text = font_medium.render(f"Distance: {int(self.distance*10):,}px", True, WHITE)
        screen.blit(distance_text, (10, 90))
        
        # Special indicator for final biome
        biome_color = (255, 100, 255) if self.current_biome == SPACE else WHITE
        biome_text = font_medium.render(f"Biome: {biome_names[self.current_biome]}", True, biome_color)
        if self.current_biome == SPACE:
            # Add special effect for space biome
            for i in range(3):
                glow_text = font_medium.render(f"Biome: {biome_names[self.current_biome]}", True, (100, 50, 255))
                screen.blit(glow_text, (12 + i, 132 + i))
        screen.blit(biome_text, (10, 130))
        
        # Coins displayed in top right
        coins_text = font_medium.render(f"Coins: {self.total_coins:,}", True, WHITE)
        screen.blit(coins_text, (SCREEN_WIDTH - 220, 10))
        
        # Draw active power-ups with timers - positioned below coins
        powerup_y = 50  # Start below coins
        for powerup_type, timer in self.powerup_timers.items():
            seconds_left = timer // 60
            max_duration = 300
            if powerup_type == "coin_magnet":
                max_duration = 600
            elif powerup_type == "speed":
                max_duration = 360
            elif powerup_type == "double_coins":
                max_duration = 480
            elif powerup_type == "shield":
                max_duration = 240
            
            bar_width = 150
            bar_height = 20
            bar_x = SCREEN_WIDTH - 200
            
            # Background bar
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, powerup_y, bar_width, bar_height))
            
            # Progress bar
            progress = timer / max_duration
            fill_width = int(bar_width * progress)
            
            colors = {
                "shield": (0, 100, 255),
                "speed": (255, 215, 0),
                "coin_magnet": (128, 0, 128),
                "double_coins": (0, 200, 0),
                "jetpack": (255, 140, 0)
            }
            color = colors.get(powerup_type, WHITE)
            pygame.draw.rect(screen, color, (bar_x, powerup_y, fill_width, bar_height))
            
            # Text label above bar
            powerup_name = powerup_type.replace("_", " ").title()
            powerup_text = font_small.render(f"{powerup_name}: {seconds_left:.1f}s", True, WHITE)
            screen.blit(powerup_text, (bar_x, powerup_y - 25))
            powerup_y += 45  # Move down for next powerup
        
        # Jetpack fuel display (if active)
        if self.player.has_jetpack:
            fuel_percent = (self.player.jetpack_fuel / self.player.max_jetpack_fuel) * 100
            fuel_text = font_small.render(f"Jetpack Fuel: {fuel_percent:.0f}%", True, ORANGE)
            screen.blit(fuel_text, (SCREEN_WIDTH - 200, powerup_y))
        
        # Enhanced mission display
        self.draw_missions(screen)
        
        # Show biome transition message
        if self.biome_transition_timer > 0:
            # Calculate fade in/out effect
            alpha = min(255, (self.biome_transition_timer / 180) * 200)
            
            # Transition message
            transition_text = font_huge.render(f"Welcome to {biome_names[self.current_biome].upper()}!", True, (255, 215, 0))
            transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
            
            # Render to temporary surface for alpha
            transition_surface = pygame.Surface((SCREEN_WIDTH, 150), pygame.SRCALPHA)
            temp_text = pygame.transform.smoothscale(transition_text, transition_text.get_size())
            transition_surface.blit(temp_text, (transition_rect.x - 100, transition_rect.y - 50))
            transition_surface.set_alpha(int(alpha))
            screen.blit(transition_surface, (0, 0))
        
        # Mission completion notification
        if self.mission_completion_timer > 0:
            self.mission_completion_timer -= 1
            glow_alpha = min(255, self.mission_completion_timer * 2)
            
            completion_surface = pygame.Surface((400, 60))
            completion_surface.fill((255, 215, 0))
            completion_surface.set_alpha(glow_alpha // 4)
            completion_rect = completion_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            screen.blit(completion_surface, completion_rect)
            
            completed_text = font_large.render("MISSION COMPLETED!", True, (255, 215, 0))
            reward_text = font_medium.render(f"+{self.missions[-1].reward if self.missions else 0} Coins!", True, WHITE)
            
            text_rect = completed_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            reward_rect = reward_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
            
            screen.blit(completed_text, text_rect)
            screen.blit(reward_text, reward_rect)

    def draw_missions(self, screen):
        """Enhanced mission display"""
        mission_y = 170
        active_missions = [m for m in self.missions if m.biome == self.current_biome][:3]
        
        if active_missions:
            header_surface = pygame.Surface((450, 35))
            header_surface.fill((0, 0, 0))
            header_surface.set_alpha(180)
            screen.blit(header_surface, (10, mission_y - 5))
            
            mission_title = font_medium.render("Current Missions:", True, YELLOW)
            screen.blit(mission_title, (15, mission_y))
            mission_y += 40
            
            for mission in active_missions:
                progress = mission.get_progress()
                
                mission_surface = pygame.Surface((450, 40))
                mission_surface.fill((0, 0, 0))
                mission_surface.set_alpha(150)
                screen.blit(mission_surface, (10, mission_y - 2))
                
                bar_width = 420
                bar_height = 30
                progress_width = int((bar_width * progress) / 100)
                
                pygame.draw.rect(screen, (30, 30, 30), (15, mission_y, bar_width, bar_height))
                
                if progress == 100:
                    color = GREEN
                elif progress > 75:
                    color = (255, 215, 0)
                elif progress > 50:
                    color = (255, 165, 0)
                else:
                    color = (100, 150, 255)
                
                pygame.draw.rect(screen, color, (15, mission_y, progress_width, bar_height))
                pygame.draw.rect(screen, WHITE, (15, mission_y, bar_width, bar_height), 2)
                
                mission_desc = f"{mission.description}"
                progress_info = f"({mission.get_progress_text()})"
                
                mission_text = font_small.render(mission_desc, True, WHITE)
                progress_text = font_small.render(progress_info, True, YELLOW)
                
                screen.blit(mission_text, (20, mission_y + 3))
                screen.blit(progress_text, (20, mission_y + 18))
                
                mission_y += 45

# Enhanced Menu Runner Animation
class MenuRunner:
    def __init__(self):
        self.frames = runner_frames
        self.current_frame = 0
        self.x = -100
        self.y = SCREEN_HEIGHT - 200
        self.speed = 3
        self.animation_timer = 0
        self.scale = 3.0  # Bigger runner for menu
        self.bounce_offset = 0
        self.direction = 1
    
    def update(self):
        # Animate across screen
        self.x += self.speed * self.direction
        
        # Bounce at edges
        if self.x > SCREEN_WIDTH + 100:
            self.direction = -1
            self.x = SCREEN_WIDTH + 100
        elif self.x < -100:
            self.direction = 1
            self.x = -100
        
        # Animate frames
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0
        
        # Bounce effect
        self.bounce_offset += 0.15
    
    def draw(self, screen):
        bounce_y = self.y + math.sin(self.bounce_offset) * 8
        scaled_frame = pygame.transform.scale(self.frames[self.current_frame], 
                                            (int(TILE_SIZE * self.scale), int(TILE_SIZE * self.scale)))
        
        # Flip sprite when moving left
        if self.direction == -1:
            scaled_frame = pygame.transform.flip(scaled_frame, True, False)
        
        screen.blit(scaled_frame, (self.x, bounce_y))

# Initialize menu runner
menu_runner = MenuRunner()

# Enhanced menu functions
def draw_menu(screen):
    """Enhanced main menu with animated runner"""
    bg_color = (15, 15, 40)
    screen.fill(bg_color)
    
    current_time = pygame.time.get_ticks()
    
    # Enhanced animated background
    for i in range(150):
        star_speed = (i % 5) + 1
        x = (current_time // (30 * star_speed) + i * 73) % SCREEN_WIDTH
        y = (math.sin(current_time / 1500 + i) * 20) + (i * 19) % SCREEN_HEIGHT
        brightness = abs(math.sin(current_time / 1200 + i)) * 180 + 75
        size = 1 + int(brightness / 180)
        color_variants = [
            (int(brightness), int(brightness), int(brightness)),
            (int(brightness), int(brightness * 0.7), int(brightness * 0.5)),
            (int(brightness * 0.5), int(brightness * 0.7), int(brightness)),
            (int(brightness * 0.7), int(brightness), int(brightness * 0.5))
        ]
        color = color_variants[i % len(color_variants)]
        pygame.draw.circle(screen, color, (int(x), int(y)), size)
    
    # Animated title with multiple effects
    title_glow = abs(math.sin(current_time / 800)) * 30 + 20
    
    # Multi-layered glow effect
    for layer in range(8):
        alpha = (8 - layer) * 20
        offset = layer * 2
        glow_color = (50 + layer * 10, 50 + layer * 5, 150 + layer * 10)
        
        title_surface = pygame.Surface((600, 100))
        title_surface.fill(glow_color)
        title_surface.set_alpha(alpha)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2 + offset, SCREEN_HEIGHT//4 + offset))
        screen.blit(title_surface, title_rect)
    
    # Main title
    title_text = font_huge.render("COSMIC RUNNER", True, WHITE)
    title_shadow = font_huge.render("COSMIC RUNNER", True, (100, 100, 100))
    
    # Title shadow
    title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 3, SCREEN_HEIGHT//4 + 3))
    screen.blit(title_shadow, title_shadow_rect)
    
    # Main title
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
    screen.blit(title_text, title_rect)
    
    # Animated subtitle with wave effect
    wave_offset = math.sin(current_time / 600) * 15
    subtitle_text = font_medium.render("Enhanced Edition - Journey Through 7 Cosmic Biomes", True, (150, 200, 255))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 80 + wave_offset))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Update and draw animated runner
    menu_runner.update()
    menu_runner.draw(screen)
    
    # Enhanced menu options with better styling
    options = [
        ("SPACE - Start Adventure", "Begin your cosmic journey"),
        ("I - Instructions & Controls", "Learn how to play"),
        ("F11 - Toggle Fullscreen", "Switch display mode"),
        ("M - Toggle Music", "Audio controls"),
        ("ESC - Exit Game", "Quit the game")
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    start_y = SCREEN_HEIGHT//2 + 50
    
    for i, (option, description) in enumerate(options):
        y_pos = start_y + i * 60
        
        # Enhanced hover detection with larger area
        option_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, y_pos - 25, 500, 50)
        is_hovering = option_rect.collidepoint(mouse_pos)
        
        # Animated background for options
        if is_hovering:
            # Pulsing glow effect
            glow_intensity = abs(math.sin(current_time / 300)) * 100 + 50
            
            for glow_layer in range(3):
                glow_surf = pygame.Surface((520, 60))
                glow_color = (50 + glow_layer * 30, 100 + glow_layer * 20, 255 - glow_layer * 30)
                glow_surf.fill(glow_color)
                glow_surf.set_alpha(int(glow_intensity / (glow_layer + 1)))
                glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, y_pos))
                screen.blit(glow_surf, glow_rect)
        
        # Option background
        option_bg = pygame.Surface((480, 45))
        bg_color = (30, 50, 100) if is_hovering else (20, 20, 40)
        option_bg.fill(bg_color)
        option_bg.set_alpha(180)
        bg_rect = option_bg.get_rect(center=(SCREEN_WIDTH//2, y_pos))
        screen.blit(option_bg, bg_rect)
        
        # Main option text
        option_color = (255, 255, 100) if is_hovering else WHITE
        option_text = font_medium.render(option, True, option_color)
        option_text_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, y_pos - 8))
        screen.blit(option_text, option_text_rect)
        
        # Description text
        desc_color = (200, 200, 200) if is_hovering else (150, 150, 150)
        desc_text = font_small.render(description, True, desc_color)
        desc_text_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, y_pos + 12))
        screen.blit(desc_text, desc_text_rect)
    
    # Enhanced celestial decorations
    # Animated moon
    moon_glow = abs(math.sin(current_time / 1000)) * 25 + 15
    for layer in range(4):
        pygame.draw.circle(screen, (80 + layer * 20, 80 + layer * 20, 150 + layer * 20), 
                          (100, 100), int(moon_glow + layer * 5))
    pygame.draw.circle(screen, MOON_COLOR, (100, 100), 40)
    # Moon craters
    pygame.draw.circle(screen, (180, 180, 180), (90, 90), 8)
    pygame.draw.circle(screen, (180, 180, 180), (110, 105), 6)
    pygame.draw.circle(screen, (180, 180, 180), (105, 85), 4)
    
    # Animated sun
    sun_glow = abs(math.cos(current_time / 900)) * 30 + 20
    sun_x, sun_y = SCREEN_WIDTH - 100, 100
    for layer in range(5):
        pygame.draw.circle(screen, (255, 200 - layer * 20, layer * 10), 
                          (sun_x, sun_y), int(sun_glow + layer * 6))
    pygame.draw.circle(screen, SUN_COLOR, (sun_x, sun_y), 45)
    # Sun rays
    for i in range(12):
        angle = math.radians(i * 30 + current_time / 50)
        ray_length = 25 + abs(math.sin(current_time / 300 + i)) * 10
        start_x = sun_x + 50 * math.cos(angle)
        start_y = sun_y + 50 * math.sin(angle)
        end_x = sun_x + (50 + ray_length) * math.cos(angle)
        end_y = sun_y + (50 + ray_length) * math.sin(angle)
        pygame.draw.line(screen, SUN_COLOR, (start_x, start_y), (end_x, end_y), 4)
    
    # Enhanced shooting stars with trails
    for i in range(3):
        star_time = (current_time + i * 2000) % 8000
        if star_time < 2000:
            progress = star_time / 2000
            start_x = SCREEN_WIDTH * (0.1 + i * 0.3)
            start_y = SCREEN_HEIGHT * (0.1 + i * 0.15)
            end_x = start_x + 200 + i * 50
            end_y = start_y + 120 + i * 30
            
            x = start_x + (end_x - start_x) * progress
            y = start_y + (end_y - start_y) * progress
            
            # Enhanced trail effect
            trail_length = 40
            for j in range(trail_length):
                trail_progress = max(0, progress - j * 0.008)
                if trail_progress > 0:
                    trail_x = start_x + (end_x - start_x) * trail_progress
                    trail_y = start_y + (end_y - start_y) * trail_progress
                    trail_alpha = max(0, 255 - j * 6)
                    trail_size = max(1, 5 - j//8)
                    
                    if trail_alpha > 0:
                        trail_colors = [
                            (255, 255, 255),
                            (255, 255, 200),
                            (255, 200, 100),
                            (200, 150, 100)
                        ]
                        color_index = min(3, j // 10)
                        pygame.draw.circle(screen, trail_colors[color_index], 
                                         (int(trail_x), int(trail_y)), trail_size)
    
    # Enhanced volume slider
    volume_slider.draw(screen, font_medium)

def draw_game_over(screen, game):
    """Draw game over screen"""
    # Semi-transparent dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((40, 0, 0))  # Dark red background
    overlay.set_alpha(220)
    screen.blit(overlay, (0, 0))
    
    current_time = pygame.time.get_ticks()
    
    # Enhanced game over text with pulsing effect
    pulse = abs(math.sin(current_time / 600)) * 50 + 50
    text_color = (255, int(pulse), int(pulse))
    
    for i in range(6):
        glow_color = (100 - i*10, 0, 0)
        glow_offset = i * 3
        glow_text = font_huge.render("GAME OVER", True, glow_color)
        glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + glow_offset, SCREEN_HEIGHT//3 + glow_offset))
        screen.blit(glow_text, glow_rect)
    
    game_over_text = font_huge.render("GAME OVER", True, text_color)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
    screen.blit(game_over_text, game_over_rect)
    
    # Special message for reaching space
    if game.current_biome == SPACE:
        space_text = font_large.render("You reached the final frontier!", True, (150, 100, 255))
        space_rect = space_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + 80))
        screen.blit(space_text, space_rect)
    
    # Enhanced stats with better formatting
    stats = [
        f"Final Score: {game.score:,}",
        f"Distance Traveled: {int(game.distance * 10):,} pixels",
        f"Total Coins Collected: {game.total_coins:,}",
        f"Biomes Explored: {game.current_biome + 1}/7",
        f"Missions Completed: {len(game.completed_missions)}",
        f"Highest Biome: {biome_names[game.current_biome]}"
    ]
    
    if game.current_biome == SPACE:
        stats.append("🚀 SPACE EXPLORER ACHIEVEMENT! 🚀")
    
    y_offset = SCREEN_HEIGHT//2 - 20
    for i, stat in enumerate(stats):
        # Stat background
        stat_bg = pygame.Surface((600, 40))
        stat_bg.fill((0, 0, 0))
        stat_bg.set_alpha(150)
        stat_rect = stat_bg.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(stat_bg, stat_rect)
        
        # Special color for achievement
        text_color = (255, 215, 0) if "ACHIEVEMENT" in stat else WHITE
        stat_text = font_medium.render(stat, True, text_color)
        stat_text_rect = stat_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(stat_text, stat_text_rect)
        y_offset += 45
    
    # Enhanced options
    y_offset += 20
    options = [
        "Press SPACE to Play Again",
        "Press ESC for Main Menu"
    ]
    
    for option in options:
        option_bg = pygame.Surface((450, 40))
        option_bg.fill((100, 50, 0))
        option_bg.set_alpha(120)
        option_rect = option_bg.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(option_bg, option_rect)
        
        option_text = font_medium.render(option, True, YELLOW)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(option_text, text_rect)
        y_offset += 50

def draw_instructions(screen):
    """Fixed instructions screen - all content fits in window"""
    screen.fill((20, 20, 50))
    
    current_time = pygame.time.get_ticks()
    
    # Animated background
    for i in range(40):
        x = (current_time // 60 + i * 120) % SCREEN_WIDTH
        y = (i * 30) % SCREEN_HEIGHT
        alpha = abs(math.sin(current_time / 1200 + i)) * 80 + 30
        pygame.draw.circle(screen, (int(alpha//4), int(alpha//4), int(alpha)), (int(x), int(y)), 3)
    
    # Title with glow
    for i in range(3):
        title_glow = font_large.render("GAME INSTRUCTIONS", True, (50 + i*30, 50 + i*20, 100 + i*50))
        title_glow_rect = title_glow.get_rect(center=(SCREEN_WIDTH//2 + i, 50 + i))
        screen.blit(title_glow, title_glow_rect)
    
    title_text = font_large.render("GAME INSTRUCTIONS", True, YELLOW)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Organized instructions - fits in window height
    left_column = [
        ("CONTROLS:", WHITE, True, 0),
        ("SPACE - Jump / Use Jetpack", (150, 200, 255), False, 0),
        ("P - Pause Game", (150, 200, 255), False, 0),
        ("M - Toggle Music", (150, 200, 255), False, 0),
        ("F11 - Toggle Fullscreen", (150, 200, 255), False, 0),
        ("", WHITE, False, 0),
        ("BIOMES:", WHITE, True, 0),
        ("Plateau → Dark Forest → Desert", (255, 200, 100), False, 0),
        ("Sea → Volcano → Sky → Space", (255, 100, 255), False, 0),
        ("", WHITE, False, 0),
        ("POWER-UPS:", WHITE, True, 0),
        ("🛡️ Shield - Absorbs hits", (100, 150, 255), False, 0),
        ("⚡ Speed - Temporary boost", (255, 215, 0), False, 0),
        ("🧲 Magnet - Attracts coins", (200, 100, 200), False, 0),
        ("🚀 Jetpack - Limited flight", (255, 140, 0), False, 0),
    ]
    
    right_column = [
        ("GAMEPLAY:", WHITE, True, 1),
        ("• Navigate 7 cosmic biomes", (200, 200, 200), False, 1),
        ("• Collect coins for score", (200, 200, 200), False, 1),
        ("• Avoid obstacles or lose life", (200, 200, 200), False, 1),
        ("• Complete biome missions", (200, 200, 200), False, 1),
        ("• Find checkpoints to save", (200, 200, 200), False, 1),
        ("", WHITE, False, 1),
        ("FEATURES:", WHITE, True, 1),
        ("• Smart obstacle spacing", (150, 255, 150), False, 1),
        ("• Animated characters", (150, 255, 150), False, 1),
        ("• Progressive difficulty", (150, 255, 150), False, 1),
        ("• Mission system", (150, 255, 150), False, 1),
        ("• Space as final challenge", (255, 150, 255), False, 1),
        ("", WHITE, False, 1),
        ("Press ESC to return", YELLOW, False, 1),
    ]
    
    # Draw left column
    y = 100
    for text, color, is_header, column in left_column:
        if text == "":
            y += 8
            continue
            
        if is_header:
            # Header background
            header_bg = pygame.Surface((SCREEN_WIDTH//2 - 40, 25))
            header_bg.fill((50, 50, 120))
            header_bg.set_alpha(180)
            screen.blit(header_bg, (20, y - 2))
        
        font_to_use = font_medium if is_header else font_small
        rendered_text = font_to_use.render(text, True, color)
        screen.blit(rendered_text, (25, y))
        
        y += 30 if is_header else 22
    
    # Draw right column
    y = 100
    for text, color, is_header, column in right_column:
        if text == "":
            y += 8
            continue
            
        if is_header:
            # Header background
            header_bg = pygame.Surface((SCREEN_WIDTH//2 - 40, 25))
            header_bg.fill((50, 50, 120))
            header_bg.set_alpha(180)
            screen.blit(header_bg, (SCREEN_WIDTH//2 + 20, y - 2))
        
        font_to_use = font_medium if is_header else font_small
        rendered_text = font_to_use.render(text, True, color)
        screen.blit(rendered_text, (SCREEN_WIDTH//2 + 25, y))
        
        y += 30 if is_header else 22
    
    # Draw volume slider
    volume_slider.draw(screen, font_medium)

def draw_pause_screen(screen):
    """Enhanced pause screen"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((30, 30, 80))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    current_time = pygame.time.get_ticks()
    glow = abs(math.sin(current_time / 400)) * 80 + 100
    
    # Enhanced glow effect
    for i in range(6):
        alpha = (6-i) * 25
        glow_text = font_huge.render("PAUSED", True, (int(glow), int(glow), 0))
        glow_surf = pygame.Surface(glow_text.get_size())
        glow_surf.fill((int(glow//3), int(glow//3), 0))
        glow_surf.set_alpha(alpha)
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2 + i*2, SCREEN_HEIGHT//2 - 80 + i*2))
        screen.blit(glow_surf, glow_rect)

    pause_text = font_huge.render("PAUSED", True, YELLOW)
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
    screen.blit(pause_text, pause_rect)

    # Enhanced options with backgrounds
    options = [
        "Press P or SPACE to Resume",
        "Press ESC to return to Menu"
    ]
    
    y_offset = SCREEN_HEIGHT//2
    for i, option in enumerate(options):
        option_bg = pygame.Surface((500, 50))
        bg_color = (60, 60, 120) if i == 0 else (50, 50, 100)
        option_bg.fill(bg_color)
        option_bg.set_alpha(150)
        option_rect = option_bg.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(option_bg, option_rect)
        
        option_text = font_large.render(option, True, WHITE)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
        screen.blit(option_text, text_rect)
        y_offset += 60
    
    # Draw volume slider
    volume_slider.draw(screen, font_medium)

def main():
    """Main game loop"""
    global SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL, volume_slider
    
    # Initialize game
    game = Game()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            # Always handle volume slider events
            volume_slider.handle_event(event)
            
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    handle_window_resize(event.size)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                
                elif event.key == pygame.K_m:
                    toggle_mute()
                
                elif event.key == pygame.K_ESCAPE:
                    if game.state == MENU:
                        running = False
                    elif game.state == INSTRUCTIONS:
                        game.state = MENU
                    elif game.state == PLAYING:
                        game.state = PAUSED
                    elif game.state == GAME_OVER:
                        game.state = MENU
                    elif game.state == PAUSED:
                        game.state = MENU
                
                elif event.key == pygame.K_SPACE:
                    if game.state == MENU:
                        game.reset_game()
                        game.state = PLAYING
                    elif game.state == PLAYING:
                        game.jump_input()
                    elif game.state == GAME_OVER:
                        game.reset_game()
                        game.state = PLAYING
                    elif game.state == PAUSED:
                        game.state = PLAYING
                
                elif event.key == pygame.K_i:
                    if game.state == MENU:
                        game.state = INSTRUCTIONS
                
                elif event.key == pygame.K_p:
                    if game.state == PLAYING:
                        game.state = PAUSED
                    elif game.state == PAUSED:
                        game.state = PLAYING
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    if game.state == PLAYING:
                        game.jump_input()
        
        # Update game logic
        if game.state == PLAYING:
            game.update()
        
        # Draw current game state
        if game.state == MENU:
            draw_menu(screen)
        elif game.state == INSTRUCTIONS:
            draw_instructions(screen)
        elif game.state == PLAYING:
            game.draw(screen)
        elif game.state == PAUSED:
            game.draw(screen)
            draw_pause_screen(screen)
        elif game.state == GAME_OVER:
            draw_game_over(screen, game)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    try:
        stop_music()
    except:
        pass
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()