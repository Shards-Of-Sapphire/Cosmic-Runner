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
REF_SCREEN_WIDTH = _initial_display_info.current_w - 100
REF_SCREEN_HEIGHT = _initial_display_info.current_h - 100
REF_GROUND_MARGIN = 100

# Current, dynamic screen dimensions
SCREEN_WIDTH = REF_SCREEN_WIDTH
SCREEN_HEIGHT = REF_SCREEN_HEIGHT
GROUND_LEVEL = SCREEN_HEIGHT - REF_GROUND_MARGIN + 75
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Runner - Celestia")

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
MOON_COLOR = (220, 220, 220)
SUN_COLOR = (255, 215, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

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
font_title = pygame.font.SysFont("Arial", 60)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Biomes - Extended to 8 biomes with day/night
FOREST = 0
SEA = 1
SNOW = 2
DESERT = 3
SKY = 4
SPACE = 5
VOLCANO = 6
CRYSTAL = 7

biome_names = ["Forest", "Sea", "Snow", "Desert", "Sky", "Space", "Volcano", "Crystal"]

# Time of day
DAY = 0
NIGHT = 1

# Tile size
TILE_SIZE = 32

# Resource path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Directories
current_dir = os.path.dirname(__file__)
bgm_path = os.path.join(current_dir, "assets", "music")
image_path = os.path.join(current_dir, "assets", "images")
sound_path = os.path.join(current_dir, "assets", "sounds")

# Load runner image
runner_image_path = os.path.join(image_path, "runner.png")
try:
    runner_image = pygame.image.load(runner_image_path)
    runner_image = pygame.transform.scale(runner_image, (TILE_SIZE * 1.5, TILE_SIZE * 1.5))
except:
    # Create default runner if image not found
    runner_image = pygame.Surface((TILE_SIZE * 1.5, TILE_SIZE * 1.5))
    runner_image.fill(RED)

# Load and set window icon
logo_image_path = os.path.join(image_path, "sapphire-logo.png")
try:
    window_icon = pygame.transform.scale(pygame.image.load(logo_image_path), (64, 64))
    pygame.display.set_icon(window_icon)
except:
    pass

# Lives and checkpoints
lives = 3
last_checkpoint_x = 150
last_checkpoint_biome = 0
biomes_with_checkpoint = set()

# Volume slider setup
volume_slider = VolumeSlider(x=50, y=20, width=200)
set_volume(volume_slider.get_volume())

# Load title screen music
try:
    title_music = os.path.join(bgm_path, "Chills.mp3")
    pygame.mixer.music.load(title_music)
    pygame.mixer.music.play(-1, fade_ms=1000)
except (pygame.error, FileNotFoundError) as e:
    print(f"Error loading title screen music: {e}")
set_volume(volume_slider.get_volume())

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
            sounds[sound_name] = pygame.mixer.Sound(sound_path)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sound {sound_file}: {e}")
            sounds[sound_name] = None
    
    return sounds

# Enhanced Background Elements for Realistic Biomes
class BackgroundElement(pygame.sprite.Sprite):
    def __init__(self, biome, time_of_day, speed):
        super().__init__()
        self.biome = biome
        self.time_of_day = time_of_day
        self.speed = speed * 0.3
        self.layer = random.choice(['back', 'mid', 'front'])
        
        if biome == FOREST:
            self.create_forest_element()
        elif biome == SEA:
            self.create_sea_element()
        elif biome == SNOW:
            self.create_snow_element()
        elif biome == DESERT:
            self.create_desert_element()
        elif biome == SKY:
            self.create_sky_element()
        elif biome == SPACE:
            self.create_space_element()
        elif biome == VOLCANO:
            self.create_volcano_element()
        else:  # CRYSTAL
            self.create_crystal_element()
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(0, 200)
        
        # Position based on layer
        if self.layer == 'back':
            self.rect.y = random.randint(50, GROUND_LEVEL - 200)
            self.speed *= 0.5
        elif self.layer == 'mid':
            self.rect.y = random.randint(GROUND_LEVEL - 200, GROUND_LEVEL - 50)
            self.speed *= 0.8
        else:  # front
            self.rect.y = GROUND_LEVEL - self.rect.height
    
    def create_forest_element(self):
        if self.layer == 'back':
            # Realistic distant mountains with atmospheric perspective
            width = random.randint(200, 400)
            height = random.randint(120, 200)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                mountain_color = (70, 120, 70)
                highlight_color = (90, 140, 90)
            else:
                mountain_color = (30, 50, 30)
                highlight_color = (40, 60, 40)
            
            # Create layered mountain silhouettes
            for layer_idx in range(3):
                layer_height = height - layer_idx * 30
                points = [
                    (0, height),
                    (width//4 + layer_idx * 20, height - layer_height//2),
                    (width//2 + layer_idx * 10, height - layer_height),
                    (3*width//4 - layer_idx * 15, height - layer_height//3),
                    (width, height)
                ]
                layer_alpha = 180 - layer_idx * 40
                layer_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.polygon(layer_surf, (*mountain_color, layer_alpha), points)
                self.image.blit(layer_surf, (0, 0))
                
        elif self.layer == 'mid':
            # Detailed trees with realistic proportions
            width = random.randint(50, 100)
            height = random.randint(150, 250)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                trunk_color = (101, 67, 33)
                bark_color = (139, 69, 19)
                leaves_color = (34, 139, 34)
                highlight_leaves = (50, 205, 50)
            else:
                trunk_color = (60, 40, 20)
                bark_color = (80, 50, 25)
                leaves_color = (20, 80, 20)
                highlight_leaves = (30, 100, 30)
            
            # Tree trunk with bark texture
            trunk_width = width // 6
            trunk_rect = (width//2 - trunk_width//2, height//3, trunk_width, 2*height//3)
            pygame.draw.rect(self.image, trunk_color, trunk_rect)
            
            # Bark lines
            for i in range(5):
                y_pos = height//3 + i * (2*height//3 // 5)
                pygame.draw.line(self.image, bark_color, 
                               (width//2 - trunk_width//3, y_pos),
                               (width//2 + trunk_width//3, y_pos), 2)
            
            # Layered canopy for depth
            canopy_layers = [
                (width//2, height//4, width//2),
                (width//3, height//3, width//3),
                (2*width//3, height//3, width//3),
                (width//2, height//5, width//4)
            ]
            
            for cx, cy, radius in canopy_layers:
                pygame.draw.circle(self.image, leaves_color, (cx, cy), radius)
                # Highlights for 3D effect
                pygame.draw.circle(self.image, highlight_leaves, 
                                 (cx - radius//3, cy - radius//3), radius//2)
                
        else:  # front
            # Forest floor details
            width = random.randint(40, 80)
            height = random.randint(25, 50)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if random.random() > 0.6:
                # Mushrooms with realistic shading
                if self.time_of_day == DAY:
                    cap_color = (180, 50, 50)
                    stem_color = (245, 245, 220)
                    spot_color = WHITE
                else:
                    cap_color = (120, 30, 30)
                    stem_color = (180, 180, 160)
                    spot_color = (200, 200, 200)
                
                # Mushroom stem
                stem_rect = (width//2 - 4, height//2, 8, height//2)
                pygame.draw.rect(self.image, stem_color, stem_rect)
                
                # Mushroom cap with gradient effect
                cap_center = (width//2, height//3)
                for radius in range(width//3, 0, -2):
                    alpha = 255 - (width//3 - radius) * 10
                    cap_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(cap_surf, (*cap_color, alpha), (radius, radius), radius)
                    self.image.blit(cap_surf, (cap_center[0]-radius, cap_center[1]-radius))
                
                # Spots
                for _ in range(random.randint(2, 4)):
                    spot_x = cap_center[0] + random.randint(-width//4, width//4)
                    spot_y = cap_center[1] + random.randint(-height//6, height//6)
                    pygame.draw.circle(self.image, spot_color, (spot_x, spot_y), 3)
            else:
                # Ferns and undergrowth
                if self.time_of_day == DAY:
                    fern_color = (0, 100, 0)
                    highlight = (50, 150, 50)
                else:
                    fern_color = (0, 60, 0)
                    highlight = (30, 90, 30)
                
                # Draw fern fronds
                for i in range(3):
                    base_x = width//2 + (i-1) * width//4
                    for j in range(height//4):
                        frond_y = height - j * 4
                        frond_width = max(2, width//3 - j)
                        pygame.draw.ellipse(self.image, fern_color, 
                                          (base_x - frond_width//2, frond_y - 3, 
                                           frond_width, 6))
    
    def create_sea_element(self):
        if self.layer == 'back':
            # Distant islands with atmospheric haze
            width = random.randint(150, 300)
            height = random.randint(40, 80)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                island_color = (100, 150, 100)
                haze_color = (200, 200, 255, 100)
            else:
                island_color = (50, 75, 50)
                haze_color = (100, 100, 150, 80)
            
            # Island silhouette with multiple peaks
            points = []
            for x in range(0, width, width//8):
                peak_height = random.randint(height//3, height)
                points.append((x, height - peak_height))
            points.append((width, height))
            points.append((0, height))
            
            pygame.draw.polygon(self.image, island_color, points)
            
            # Atmospheric haze effect
            haze_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(haze_surf, haze_color, (0, 0, width, height))
            self.image.blit(haze_surf, (0, 0))
            
        elif self.layer == 'mid':
            # Realistic waves with foam and spray
            width = random.randint(100, 200)
            height = random.randint(30, 60)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                deep_water = (0, 100, 150)
                wave_color = (70, 130, 180)
                foam_color = WHITE
                spray_color = (200, 200, 255, 100)
            else:
                deep_water = (0, 50, 80)
                wave_color = (30, 60, 90)
                foam_color = (200, 200, 200)
                spray_color = (150, 150, 200, 80)
            
            # Wave base
            wave_points = []
            for x in range(width):
                wave_height = height//2 + int(math.sin(x * 0.1) * height//4)
                wave_points.append((x, wave_height))
            wave_points.append((width, height))
            wave_points.append((0, height))
            
            pygame.draw.polygon(self.image, wave_color, wave_points)
            
            # Wave crest foam
            crest_y = min(point[1] for point in wave_points[:-2])
            foam_rect = (0, crest_y - 5, width, 15)
            pygame.draw.ellipse(self.image, foam_color, foam_rect)
            
            # Water spray particles
            spray_surf = pygame.Surface((width, height//2), pygame.SRCALPHA)
            for _ in range(10):
                spray_x = random.randint(0, width)
                spray_y = random.randint(0, height//3)
                pygame.draw.circle(spray_surf, spray_color, (spray_x, spray_y), 2)
            self.image.blit(spray_surf, (0, 0))
            
        else:  # front
            # Detailed seaweed and coral
            width = random.randint(30, 60)
            height = random.randint(60, 120)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if random.random() > 0.5:
                # Coral formation
                if self.time_of_day == DAY:
                    coral_colors = [(255, 127, 80), (255, 99, 71), (255, 160, 122)]
                else:
                    coral_colors = [(180, 90, 60), (180, 70, 50), (180, 110, 80)]
                
                base_color = random.choice(coral_colors)
                
                # Coral base
                base_rect = (width//4, height//2, width//2, height//2)
                pygame.draw.ellipse(self.image, base_color, base_rect)
                
                # Coral branches with organic curves
                for _ in range(random.randint(3, 6)):
                    branch_points = []
                    start_x = width//2 + random.randint(-width//6, width//6)
                    start_y = height//2
                    
                    for segment in range(5):
                        x = start_x + random.randint(-10, 10)
                        y = start_y - segment * height//8
                        branch_points.append((x, y))
                    
                    if len(branch_points) > 1:
                        pygame.draw.lines(self.image, base_color, False, branch_points, 4)
            else:
                # Swaying seaweed
                if self.time_of_day == DAY:
                    seaweed_color = (0, 128, 0)
                    highlight_color = (50, 180, 50)
                else:
                    seaweed_color = (0, 80, 0)
                    highlight_color = (30, 120, 30)
                
                # Multiple seaweed strands
                for strand in range(3):
                    strand_x = width//4 + strand * width//4
                    points = []
                    
                    for y in range(0, height, height//10):
                        curve_x = strand_x + int(math.sin(y * 0.1) * 8)
                        points.append((curve_x, height - y))
                    
                    if len(points) > 1:
                        pygame.draw.lines(self.image, seaweed_color, False, points, 6)
                        pygame.draw.lines(self.image, highlight_color, False, points, 2)
    
    def create_snow_element(self):
        if self.layer == 'back':
            # Snow-capped mountain ranges with realistic lighting
            width = random.randint(250, 450)
            height = random.randint(150, 250)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                mountain_color = (150, 150, 170)
                shadow_color = (120, 120, 140)
                snow_color = (255, 255, 255)
                snow_shadow = (230, 230, 250)
            else:
                mountain_color = (80, 80, 100)
                shadow_color = (60, 60, 80)
                snow_color = (200, 200, 220)
                snow_shadow = (170, 170, 190)
            
            # Create mountain silhouette with multiple peaks
            peaks = []
            for i in range(5):
                peak_x = i * width // 4
                peak_y = random.randint(height//4, height//2)
                peaks.append((peak_x, peak_y))
            
            mountain_points = [(0, height)]
            mountain_points.extend(peaks)
            mountain_points.append((width, height))
            
            pygame.draw.polygon(self.image, mountain_color, mountain_points)
            
            # Add shadows on the right side of peaks
            shadow_points = [(0, height)]
            for i, (px, py) in enumerate(peaks[:-1]):
                next_px, next_py = peaks[i+1]
                if next_py > py:  # Shadow side
                    shadow_points.extend([(px, py), (next_px, next_py)])
            shadow_points.append((width, height))
            
            shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            if len(shadow_points) > 3:
                pygame.draw.polygon(shadow_surf, (*shadow_color, 120), shadow_points)
                self.image.blit(shadow_surf, (0, 0))
            
            # Snow caps on peaks
            for px, py in peaks:
                if py < height//2:  # Only high peaks get snow
                    snow_points = [
                        (px, py),
                        (px - 30, py + 40),
                        (px + 30, py + 40)
                    ]
                    pygame.draw.polygon(self.image, snow_color, snow_points)
                    # Snow highlight
                    highlight_points = [
                        (px, py),
                        (px - 15, py + 20),
                        (px + 15, py + 20)
                    ]
                    pygame.draw.polygon(self.image, snow_shadow, highlight_points)
            
        elif self.layer == 'mid':
            # Detailed evergreen trees with snow
            width = random.randint(40, 80)
            height = random.randint(120, 200)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                trunk_color = (101, 67, 33)
                tree_color = (0, 100, 0)
                snow_color = (255, 255, 255)
            else:
                trunk_color = (60, 40, 20)
                tree_color = (0, 60, 0)
                snow_color = (200, 200, 220)
            
            # Tree trunk
            trunk_rect = (width//2 - 4, height//2, 8, height//2)
            pygame.draw.rect(self.image, trunk_color, trunk_rect)
            
            # Evergreen tree layers from bottom to top
            for layer in range(4):
                layer_y = height//2 - layer * 25
                layer_width = width - layer * 8
                
                # Tree layer (triangle)
                tree_points = [
                    (width//2, layer_y - 30),
                    (width//2 - layer_width//2, layer_y),
                    (width//2 + layer_width//2, layer_y)
                ]
                pygame.draw.polygon(self.image, tree_color, tree_points)
                
                # Snow on branches
                snow_points = [
                    (width//2, layer_y - 25),
                    (width//2 - layer_width//3, layer_y - 5),
                    (width//2 + layer_width//3, layer_y - 5)
                ]
                pygame.draw.polygon(self.image, snow_color, snow_points)
            
        else:  # front
            # Snow drifts, rocks, and winter plants
            width = random.randint(50, 100)
            height = random.randint(20, 40)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            element_type = random.choice(['drift', 'rock', 'bush'])
            
            if element_type == 'drift':
                if self.time_of_day == DAY:
                    snow_color = (255, 255, 255)
                    shadow_color = (240, 240, 255)
                else:
                    snow_color = (200, 200, 220)
                    shadow_color = (180, 180, 200)
                
                # Snow drift with realistic shading
                pygame.draw.ellipse(self.image, snow_color, (0, 0, width, height))
                pygame.draw.ellipse(self.image, shadow_color, (width//4, height//4, width//2, height//2))
                
                # Sparkles in daylight
                if self.time_of_day == DAY:
                    for _ in range(8):
                        sx = random.randint(0, width)
                        sy = random.randint(0, height)
                        pygame.draw.circle(self.image, (255, 255, 255), (sx, sy), 1)
                        
            elif element_type == 'rock':
                if self.time_of_day == DAY:
                    rock_color = (100, 100, 120)
                    snow_color = (255, 255, 255)
                else:
                    rock_color = (60, 60, 80)
                    snow_color = (200, 200, 220)
                
                # Rock partially covered in snow
                pygame.draw.ellipse(self.image, rock_color, 
                                  (width//6, height//3, 2*width//3, 2*height//3))
                pygame.draw.ellipse(self.image, snow_color, 
                                  (width//4, height//6, width//2, height//3))
                
            else:  # bush
                if self.time_of_day == DAY:
                    bush_color = (100, 50, 0)
                    snow_color = (255, 255, 255)
                else:
                    bush_color = (60, 30, 0)
                    snow_color = (200, 200, 220)
                
                # Winter bush with snow
                for branch in range(5):
                    bx = width//2 + random.randint(-width//3, width//3)
                    by = height - random.randint(5, height//2)
                    pygame.draw.circle(self.image, bush_color, (bx, by), 3)
                    pygame.draw.circle(self.image, snow_color, (bx, by-2), 2)
    
    def create_desert_element(self):
        """Create desert background elements"""
        if self.layer == 'back':
            # Desert mountains
            width = random.randint(200, 400)
            height = random.randint(100, 180)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if self.time_of_day == DAY:
                mountain_color = (238, 203, 173)
                shadow_color = (208, 173, 143)
            else:
                mountain_color = (158, 123, 93)
                shadow_color = (128, 93, 63)
            
            # Create mountain silhouette
            points = [(0, height)]
            for x in range(0, width, width//6):
                peak_height = random.randint(height//3, height)
                points.append((x, height - peak_height))
            points.append((width, height))
            
            pygame.draw.polygon(self.image, mountain_color, points)
            
            # Add shadows
            shadow_points = [(p[0] + 10, p[1] + 10) for p in points[:-1]]
            shadow_points.append((width, height))
            shadow_points.append((0, height))
            pygame.draw.polygon(self.image, shadow_color, shadow_points)
        
        elif self.layer == 'mid':
            # Cacti or rock formations
            width = random.randint(40, 80)
            height = random.randint(80, 150)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            
            if random.random() > 0.5:
                # Cactus
                if self.time_of_day == DAY:
                    cactus_color = (50, 120, 50)
                    highlight = (70, 140, 70)
                else:
                    cactus_color = (30, 80, 30)
                    highlight = (40, 100, 40)
                
                # Main body
                pygame.draw.rect(self.image, cactus_color, (width//2 - 8, height//4, 16, height))
                pygame.draw.rect(self.image, highlight, (width//2 - 6, height//4, 4, height))
                
                # Arms
                for _ in range(2):
                    arm_y = random.randint(height//3, 2*height//3)
                    arm_width = random.randint(20, 40)
                    arm_height = random.randint(30, 50)
                    arm_x = width//2 + random.choice([-arm_width, 0])
                    
                    pygame.draw.rect(self.image, cactus_color, (arm_x, arm_y, arm_width, 12))
                    pygame.draw.rect(self.image, highlight, (arm_x + 2, arm_y, arm_width - 4, 4))
                
            else:
                # Rock formation
                if self.time_of_day == DAY:
                    rock_color = (218, 183, 153)
                    shadow = (188, 153, 123)
                else:
                    rock_color = (148, 113, 83)
                    shadow = (118, 83, 53)
                
                points = []
                for x in range(0, width, width//4):
                    points.append((x, height - random.randint(height//4, 3*height//4)))
                points.append((width, height))
                points.append((0, height))
                
                pygame.draw.polygon(self.image, rock_color, points)
                
                # Add shadows
                shadow_points = [(p[0] + 5, p[1] + 5) for p in points[:-2]]
                shadow_points.append((width, height))
                shadow_points.append((0, height))
                pygame.draw.polygon(self.image, shadow, shadow_points)
            
        else:  # front
        # Desert ground details
         width = random.randint(30, 60)
        height = random.randint(20, 40)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if self.time_of_day == DAY:
            sand_color = (238, 203, 173)
            detail_color = (208, 173, 143)
        else:
            sand_color = (158, 123, 93)
            detail_color = (128, 93, 63)
        
        # Sand dune
        pygame.draw.ellipse(self.image, sand_color, (0, height//2, width, height//2))
        pygame.draw.ellipse(self.image, detail_color, (width//4, 3*height//4, width//2, height//4))

def create_sky_element(self):
    """Create sky background elements"""
    if self.layer == 'back':
        # Clouds
        width = random.randint(100, 200)
        height = random.randint(40, 80)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if self.time_of_day == DAY:
            cloud_color = (255, 255, 255, 180)
            highlight = (255, 255, 255, 220)
        else:
            cloud_color = (100, 100, 150, 180)
            highlight = (120, 120, 170, 220)
        
        # Create puffy cloud shapes
        centers = [(width//4, height//2), (width//2, height//2), (3*width//4, height//2)]
        for cx, cy in centers:
            pygame.draw.circle(self.image, cloud_color, (cx, cy), height//2)
            pygame.draw.circle(self.image, highlight, (cx, cy - height//4), height//3)

def create_space_element(self):
    """Create space background elements"""
    if self.layer == 'back':
        # Stars and nebulas
        width = random.randint(100, 200)
        height = random.randint(100, 200)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create stars
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            alpha = random.randint(150, 255)
            pygame.draw.circle(self.image, (*WHITE[:3], alpha), (x, y), size)

def create_volcano_element(self):
    """Create volcano background elements"""
    if self.layer == 'back':
        # Volcano shape
        width = random.randint(200, 400)
        height = random.randint(150, 300)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        volcano_color = (139, 69, 19)
        lava_color = (255, 69, 0)
        
        # Main volcano shape
        points = [(0, height), (width//2, 0), (width, height)]
        pygame.draw.polygon(self.image, volcano_color, points)
        
        # Lava flow
        lava_points = [(width//2, 0)]
        for _ in range(5):
            x = width//2 + random.randint(-20, 20)
            y = random.randint(0, height)
            lava_points.append((x, y))
        pygame.draw.lines(self.image, lava_color, False, lava_points, 4)

def create_crystal_element(self):
    """Create crystal cave background elements"""
    if self.layer == 'back':
        # Crystal formations
        width = random.randint(50, 100)
        height = random.randint(80, 160)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        crystal_color = (138, 43, 226)  # Purple
        highlight = (200, 100, 255)
        
        # Create crystal shapes
        for _ in range(3):
            x = random.randint(0, width)
            crystal_height = random.randint(height//2, height)
            points = [
                (x, height),
                (x - 10, height - crystal_height),
                (x + 10, height - crystal_height - 20),
                (x + 20, height)
            ]
            pygame.draw.polygon(self.image, crystal_color, points)
            
            # Add highlight
            highlight_points = [
                (x + 5, height - crystal_height + 10),
                (x + 10, height - crystal_height - 10),
                (x + 15, height - crystal_height + 10)
            ]
            pygame.draw.polygon(self.image, highlight, highlight_points)
    
    def update(self):
        self.rect.x -= self.speed
        return self.rect.right < -100

# Enhanced Mission System
class Mission:
    def __init__(self, biome, difficulty_multiplier=1.0):
        self.completed = False
        self.failed = False
        self.biome = biome
        self.time_created = time.time()
        self.progress = 0
        self.target = 0
        self.player_hit = False
        self.mission_active = True
        
        # Mission types based on biome
        mission_types = {
            FOREST: ["collect_coins", "avoid_obstacles", "survive_time"],
            SEA: ["collect_coins", "perfect_run", "speed_run"],
            SNOW: ["survive_time", "collect_coins", "avoid_obstacles"],
            DESERT: ["perfect_run", "collect_coins", "speed_run"],
            SKY: ["collect_coins", "survive_time", "perfect_run"],
            SPACE: ["avoid_obstacles", "perfect_run", "speed_run"],
            VOLCANO: ["survive_time", "perfect_run", "avoid_obstacles"],
            CRYSTAL: ["collect_coins", "speed_run", "perfect_run"]
        }
        
        self.mission_type = random.choice(mission_types.get(biome, ["collect_coins"]))
        
        # Set targets based on mission type and biome difficulty
        base_difficulty = max(1, (biome + 1) * difficulty_multiplier)
        
        if self.mission_type == "collect_coins":
            self.target = int(5 + (2 * base_difficulty))
            self.description = f"Collect {self.target} coins"
            self.reward = int(50 * base_difficulty)
        elif self.mission_type == "avoid_obstacles":
            self.target = int(3 + (1 * base_difficulty))
            self.description = f"Avoid {self.target} obstacles"
            self.reward = int(75 * base_difficulty)
        elif self.mission_type == "survive_time":
            self.target = int(8 + (3 * base_difficulty))
            self.description = f"Survive {self.target} seconds"
            self.reward = int(100 * base_difficulty)
        elif self.mission_type == "perfect_run":
            self.target = int(10 + (5 * base_difficulty))
            self.description = f"Perfect run for {self.target}s"
            self.reward = int(200 * base_difficulty)
        else:  # speed_run
            self.target = int(50 + (25 * base_difficulty))
            self.description = f"Score {self.target} points quickly"
            self.reward = int(150 * base_difficulty)
    
    def update(self, current_biome, delta_coins=0, delta_obstacles=0, delta_time=1/60, 
               player_hit=False, current_score=0, start_score=0):
        
        # Check if we're still in the correct biome
        if current_biome != self.biome and self.mission_active:
            self.mission_active = False
            return False
        
        if not self.mission_active or self.completed or self.failed:
            return False
        
        # Track if player was hit for perfect run missions
        if player_hit:
            self.player_hit = True
        
        if self.mission_type == "collect_coins":
            self.progress += delta_coins
            if self.progress >= self.target:
                self.completed = True
                return True
        elif self.mission_type == "avoid_obstacles":
            self.progress += delta_obstacles
            if self.progress >= self.target:
                self.completed = True
                return True
        elif self.mission_type == "survive_time":
            self.progress += delta_time
            if self.progress >= self.target:
                self.completed = True
                return True
        elif self.mission_type == "perfect_run":
            if self.player_hit:
                self.failed = True
                return False
            self.progress += delta_time
            if self.progress >= self.target:
                self.completed = True
                return True
        elif self.mission_type == "speed_run":
            score_gained = current_score - start_score
            self.progress = score_gained
            if score_gained >= self.target:
                self.completed = True
                return True
        
        return False
    
    def get_progress_percentage(self):
        if self.target == 0:
            return 100
        return min(100, int((self.progress / self.target) * 100))
    
    def get_progress_text(self):
        if self.mission_type == "collect_coins":
            return f"{int(self.progress)}/{self.target} coins"
        elif self.mission_type == "avoid_obstacles":
            return f"{int(self.progress)}/{self.target} avoided"
        elif self.mission_type == "survive_time":
            return f"{int(self.progress):.1f}/{self.target}s"
        elif self.mission_type == "perfect_run":
            return f"{int(self.progress):.1f}/{self.target}s perfect"
        else:  # speed_run
            return f"{int(self.progress)}/{self.target} points"

# Player class with improved jetpack and shield
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = runner_image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.y = GROUND_LEVEL - self.rect.height
        self.jumping = False
        self.velocity_y = 0
        self.is_alive = True
        self.frame = 0
        self.animation_frames = 8
        self.animation_timer = 0
        self.animation_cooldown = 5
        self.game = None
        self.jetpack_fuel = 0
        self.max_jetpack_fuel = 180  # 3 seconds at 60 FPS
        self.shield_active = False
        self.invulnerable_timer = 0  # Invulnerability frames after hit
        
        # Load sounds
        self.sounds = load_sounds()
    
    def update(self, obstacles, coins, powerups):
        player_hit = False
        
        # Update invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        
        # Handle jetpack physics
        if self.game and self.game.active_powerups["jetpack"] and self.jetpack_fuel > 0:
            # Jetpack active - counter gravity and provide lift
            self.velocity_y = max(-12, self.velocity_y - 1.5)  # More responsive jetpack
            self.jetpack_fuel -= 1
            self.jumping = True
            
            # Create jetpack particles
            if random.random() > 0.6:
                self.game.create_jetpack_particle(self.rect.centerx - 15, self.rect.bottom - 5)
        
        # Regular gravity and jumping physics
        if self.jumping:
            if not (self.game and self.game.active_powerups["jetpack"] and self.jetpack_fuel > 0):
                self.velocity_y += 0.8  # Gravity
            self.rect.y += int(self.velocity_y)
            
            # Check if landed
            if self.rect.y >= GROUND_LEVEL - self.rect.height:
                self.rect.y = GROUND_LEVEL - self.rect.height
                self.jumping = False
                self.velocity_y = 0
        
        # Keep player within screen bounds
        if self.rect.y < 0:
            self.rect.y = 0
            self.velocity_y = max(0, self.velocity_y)
        
        # Update shield visual
        self.shield_active = self.game and self.game.active_powerups["shield"]
        
        # Collision with obstacles
        if self.invulnerable_timer == 0:  # Only check collision if not invulnerable
            for obstacle in list(obstacles):
                if self.rect.colliderect(obstacle.rect):
                    if self.shield_active:
                        if self.sounds["shield"]:
                            self.sounds["shield"].play()
                        obstacles.remove(obstacle)  # Shield destroys obstacle
                        continue
                    
                    # Player hit
                    if self.sounds["death"]:
                        self.sounds["death"].play()
                    player_hit = True
                    self.lose_life()
                    break
        
        # Collect coins
        coins_collected = 0
        for coin in list(coins):
            if self.rect.colliderect(coin.rect):
                coins.remove(coin)
                coins_collected += 1
                if self.sounds["coin"]:
                    self.sounds["coin"].play()
        
        # Collect powerups
        for powerup in list(powerups):
            if self.rect.colliderect(powerup.rect):
                powerups.remove(powerup)
                self.game.activate_powerup(powerup.power_type)
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_cooldown:
            self.frame = (self.frame + 1) % self.animation_frames
            self.animation_timer = 0
        
        return coins_collected, player_hit
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
            if self.sounds["jump"]:
                self.sounds["jump"].play()
    
    def activate_jetpack(self, fuel_amount):
        self.jetpack_fuel = fuel_amount
    
    def lose_life(self):
        if self.game:
            self.game.lives -= 1
            self.invulnerable_timer = 120  # 2 seconds of invulnerability
            
            if self.game.lives <= 0:
                self.is_alive = False
                self.game.state = GAME_OVER
            else:
                # Reset position but keep running
                self.jumping = False
                self.velocity_y = 0
                self.rect.y = GROUND_LEVEL - self.rect.height
    
    def draw_shield(self, screen):
        if self.shield_active:
            # Draw animated shield halo around player
            shield_center = (self.rect.centerx, self.rect.centery)
            shield_radius = max(self.rect.width, self.rect.height) // 2 + 20
            
            # Animated shield effect with pulsing
            time_factor = pygame.time.get_ticks() * 0.008
            pulse = 1.0 + 0.3 * math.sin(time_factor * 2)
            alpha = int(80 + 40 * math.sin(time_factor))
            
            # Create shield surface
            shield_size = int(shield_radius * pulse * 2 + 20)
            shield_surf = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
            center = shield_size // 2
            
            # Draw multiple shield rings for depth
            for i in range(4):
                ring_radius = int(shield_radius * pulse) - i * 4
                ring_alpha = max(20, alpha - i * 20)
                ring_color = (*CYAN[:3], ring_alpha)
                
                if ring_radius > 0:
                    pygame.draw.circle(shield_surf, ring_color, (center, center), ring_radius, 3)
            
            # Add sparkle effects
            for i in range(8):
                angle = time_factor + i * (math.pi / 4)
                sparkle_x = center + int(shield_radius * pulse * 0.8 * math.cos(angle))
                sparkle_y = center + int(shield_radius * pulse * 0.8 * math.sin(angle))
                sparkle_color = (*WHITE[:3], alpha)
                pygame.draw.circle(shield_surf, sparkle_color, (sparkle_x, sparkle_y), 2)
            
            # Blit shield to screen
            shield_rect = shield_surf.get_rect(center=shield_center)
            screen.blit(shield_surf, shield_rect)
    
    def draw_invulnerability(self, screen):
        # Flash effect during invulnerability
        if self.invulnerable_timer > 0:
            flash_alpha = int(100 * (math.sin(self.invulnerable_timer * 0.3) * 0.5 + 0.5))
            flash_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            flash_surf.fill((*WHITE[:3], flash_alpha))
            screen.blit(flash_surf, self.rect)

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + self.gravity)  # Add gravity and air resistance
        self.lifetime -= 1
        return self.lifetime <= 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            size = max(1, int(4 * (self.lifetime / self.max_lifetime)))
            color_with_alpha = (*self.color[:3], alpha)
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            screen.blit(particle_surf, (int(self.x) - size, int(self.y) - size))

# Enhanced Obstacle class with better biome-specific obstacles
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, biome, speed):
        super().__init__()
        self.biome = biome
        self.speed = speed
        self.create_obstacle()
    
    def create_obstacle(self):
        # Enhanced obstacles based on biome with better visuals
        obstacle_types = {
            FOREST: ["log", "rock", "tree_branch", "mushroom"],
            SEA: ["wave", "coral", "jellyfish", "seaweed"],
            SNOW: ["ice_block", "snowball", "icicle", "frozen_log"],
            DESERT: ["cactus", "rock", "tumbleweed", "quicksand"],
            SKY: ["cloud", "bird", "lightning", "wind_gust"],
            SPACE: ["asteroid", "debris", "satellite", "meteor"],
            VOLCANO: ["lava_rock", "fire_burst", "hot_gas", "magma_pool"],
            CRYSTAL: ["crystal_spike", "gem_wall", "prism", "shard_cluster"]
        }
        
        self.type = random.choice(obstacle_types.get(self.biome, ["generic"]))
        self.create_visual()
    
    def create_visual(self):
        # Create detailed visuals for each obstacle type
        if self.biome == FOREST:
            if self.type == "log":
                self.image = pygame.Surface((60, 30), pygame.SRCALPHA)
                # Wood base
                pygame.draw.ellipse(self.image, (139, 69, 19), (0, 0, 60, 30))
                # Wood grain lines
                for i in range(5):
                    x_pos = i * 12
                    pygame.draw.line(self.image, (101, 67, 33), (x_pos, 5), (x_pos, 25), 2)
                # Wood rings on ends
                pygame.draw.ellipse(self.image, (160, 82, 45), (0, 5, 12, 20))
                pygame.draw.ellipse(self.image, (160, 82, 45), (48, 5, 12, 20))
                
            elif self.type == "rock":
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
                # Rock body with shading
                pygame.draw.ellipse(self.image, (105, 105, 105), (0, 0, 40, 40))
                pygame.draw.ellipse(self.image, (128, 128, 128), (5, 5, 25, 25))
                pygame.draw.ellipse(self.image, (90, 90, 90), (25, 25, 12, 12))
                # Moss patches
                pygame.draw.ellipse(self.image, (0, 100, 0), (8, 12, 8, 6))
                
            elif self.type == "mushroom":
                self.image = pygame.Surface((35, 50), pygame.SRCALPHA)
                # Stem
                pygame.draw.rect(self.image, (245, 245, 220), (13, 25, 9, 25))
                # Cap with gradient
                for radius in range(15, 0, -1):
                    alpha = 255 - (15 - radius) * 8
                    cap_color = (*[200, 50, 50], alpha)
                    pygame.draw.circle(self.image, cap_color, (17, 20), radius)
                # White spots
                spots = [(12, 15), (20, 12), (23, 18)]
                for spot in spots:
                    pygame.draw.circle(self.image, WHITE, spot, 3)
                    
            else:  # tree_branch
                self.image = pygame.Surface((70, 80), pygame.SRCALPHA)
                # Main branch
                pygame.draw.rect(self.image, (101, 67, 33), (30, 0, 10, 80))
                # Leaves clusters
                leaf_positions = [(20, 15), (45, 20), (25, 40), (50, 45), (30, 65)]
                for lx, ly in leaf_positions:
                    pygame.draw.circle(self.image, (34, 139, 34), (lx, ly), 12)
                    pygame.draw.circle(self.image, (0, 128, 0), (lx-4, ly-4), 8)
        
        elif self.biome == SEA:
            if self.type == "wave":
                self.image = pygame.Surface((80, 50), pygame.SRCALPHA)
                # Wave body with transparency
                wave_color = (70, 130, 180, 200)
                foam_color = (255, 255, 255, 180)
                
                # Main wave shape
                wave_points = [(0, 35), (20, 25), (40, 20), (60, 25), (80, 35), (80, 50), (0, 50)]
                pygame.draw.polygon(self.image, wave_color, wave_points)
                
                # Foam crest
                foam_points = [(15, 25), (25, 20), (35, 18), (45, 20), (55, 25)]
                for i, (fx, fy) in enumerate(foam_points):
                    pygame.draw.circle(self.image, foam_color, (fx, fy), 4)
                    
            elif self.type == "jellyfish":
                self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
                # Jellyfish bell
                bell_color = (255, 20, 147, 160)
                pygame.draw.ellipse(self.image, bell_color, (5, 0, 30, 25))
                # Inner bell highlight
                pygame.draw.ellipse(self.image, (255, 100, 200, 100), (8, 3, 24, 18))
                # Tentacles
                tentacle_color = (255, 20, 147, 200)
                for i in range(6):
                    start_x = 8 + i * 4
                    end_x = start_x + random.randint(-5, 5)
                    pygame.draw.line(self.image, tentacle_color, 
                                   (start_x, 25), (end_x, 55), 3)
                    
            else:  # coral or seaweed
                self.image = pygame.Surface((35, 70), pygame.SRCALPHA)
                if self.type == "coral":
                    # Coral branches
                    coral_color = (255, 127, 80)
                    pygame.draw.rect(self.image, coral_color, (15, 35, 8, 35))
                    # Coral formations
                    branch_points = [(10, 50), (25, 45), (12, 30), (28, 35)]
                    for bx, by in branch_points:
                        pygame.draw.circle(self.image, coral_color, (bx, by), 6)
                        pygame.draw.circle(self.image, (255, 160, 122), (bx-2, by-2), 4)
                else:  # seaweed
                    seaweed_color = (0, 128, 0)
                    # Swaying seaweed strands
                    for strand in range(3):
                        points = []
                        base_x = 12 + strand * 6
                        for y in range(10):
                            curve_x = base_x + int(math.sin(y * 0.3) * 4)
                            points.append((curve_x, 70 - y * 6))
                        if len(points) > 1:
                            pygame.draw.lines(self.image, seaweed_color, False, points, 4)
        
        # Add similar detailed implementations for other biomes
        elif self.biome == SNOW:
            if self.type == "ice_block":
                self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
                # Ice block with internal reflections
                ice_color = (173, 216, 230, 200)
                pygame.draw.rect(self.image, ice_color, (0, 0, 50, 50))
                # Internal highlights
                pygame.draw.polygon(self.image, (255, 255, 255, 150), 
                                  [(10, 10), (40, 10), (35, 20), (15, 20)])
                pygame.draw.polygon(self.image, (200, 200, 255, 100), 
                                  [(5, 45), (20, 30), (35, 35), (45, 45)])
                                  
            elif self.type == "icicle":
                self.image = pygame.Surface((20, 80), pygame.SRCALPHA)
                # Icicle with realistic shape and highlights
                ice_color = (173, 216, 230)
                highlight_color = (255, 255, 255)
                
                icicle_points = [(10, 0), (5, 60), (10, 80), (15, 60)]
                pygame.draw.polygon(self.image, ice_color, icicle_points)
                # Highlight ridge
                pygame.draw.polygon(self.image, highlight_color, 
                                  [(10, 0), (8, 50), (10, 70), (12, 50)])
                                  
            else:  # snowball or frozen_log
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
                if self.type == "snowball":
                    # Snowball with texture
                    pygame.draw.circle(self.image, (255, 255, 255), (20, 20), 20)
                    pygame.draw.circle(self.image, (240, 240, 255), (20, 20), 17)
                    # Snow texture
                    for _ in range(8):
                        sx = random.randint(5, 35)
                        sy = random.randint(5, 35)
                        if (sx - 20)**2 + (sy - 20)**2 <= 400:  # Inside circle
                            pygame.draw.circle(self.image, (250, 250, 250), (sx, sy), 1)
                else:  # frozen_log
                    # Log with ice coating
                    pygame.draw.ellipse(self.image, (101, 67, 33), (0, 10, 40, 20))
                    pygame.draw.ellipse(self.image, (173, 216, 230, 150), (0, 8, 40, 24))
        
        else:
            # Generic obstacle for other biomes (simplified for brevity)
            size = random.randint(30, 50)
            self.image = pygame.Surface((size, size))
            
            # Color based on biome
            colors = {
                DESERT: (238, 203, 173),
                SKY: (200, 200, 255),
                SPACE: (128, 128, 128),
                VOLCANO: (139, 69, 19),
                CRYSTAL: (138, 43, 226)
            }
            self.image.fill(colors.get(self.biome, RED))
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = GROUND_LEVEL - self.rect.height
    
    def update(self):
        self.rect.x -= self.speed
        return self.rect.right < 0

# Enhanced Coin class with better animation
class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.create_coin_image()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(GROUND_LEVEL - 150, GROUND_LEVEL - 30)
        self.speed = speed
        self.angle = 0
        self.float_offset = 0
        self.original_y = self.rect.y
        self.pulse_timer = 0
    
    def create_coin_image(self):
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        # Outer ring with gradient
        for radius in range(14, 8, -1):
            alpha = 255 - (14 - radius) * 20
            color = (*ORANGE[:3], alpha)
            pygame.draw.circle(self.image, color, (14, 14), radius)
        
        # Inner golden area
        pygame.draw.circle(self.image, YELLOW, (14, 14), 10)
        pygame.draw.circle(self.image, (255, 215, 0), (14, 14), 8)
        
        # Shine effect
        pygame.draw.circle(self.image, WHITE, (11, 11), 4)
        pygame.draw.circle(self.image, (255, 255, 200), (14, 14), 6, 2)
        
        # Dollar sign or gem symbol
        pygame.draw.line(self.image, (200, 150, 0), (14, 6), (14, 22), 2)
        pygame.draw.arc(self.image, (200, 150, 0), (9, 8, 10, 8), 0, math.pi, 2)
        pygame.draw.arc(self.image, (200, 150, 0), (9, 12, 10, 8), math.pi, 2*math.pi, 2)
    
    def update(self):
        self.rect.x -= self.speed
        # Enhanced floating animation
        self.float_offset += 0.12
        self.rect.y = int(self.original_y + math.sin(self.float_offset) * 10)
        
        # Pulsing glow effect
        self.pulse_timer += 0.08
        
        # Rotation effect
        self.angle = (self.angle + 2) % 360
        return self.rect.right < 0
    
    def draw_glow(self, screen):
        # Draw glowing effect around coin
        glow_intensity = int(30 + 20 * math.sin(self.pulse_timer))
        glow_color = (*YELLOW[:3], glow_intensity)
        
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (20, 20), 16)
        glow_rect = glow_surf.get_rect(center=self.rect.center)
        screen.blit(glow_surf, glow_rect)

# Enhanced Power-up class with better effects
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.power_type = random.choice(["shield", "jetpack", "magnet", "slowtime"])
        self.speed = speed
        self.create_powerup_image()
        
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(100, 300)
        self.rect.y = random.randint(GROUND_LEVEL - 150, GROUND_LEVEL - 30)
        self.float_offset = 0
        self.float_speed = 0.08
        self.glow_phase = 0
        self.original_y = self.rect.y
    
    def create_powerup_image(self):
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        if self.power_type == "shield":
            # Enhanced shield design
            # Outer ring
            pygame.draw.circle(self.image, CYAN, (20, 20), 20, 3)
            pygame.draw.circle(self.image, (0, 200, 255), (20, 20), 16, 2)
            # Inner shield pattern
            pygame.draw.circle(self.image, (100, 200, 255), (20, 20), 12)
            # Cross pattern
            pygame.draw.line(self.image, WHITE, (20, 8), (20, 32), 3)
            pygame.draw.line(self.image, WHITE, (8, 20), (32, 20), 3)
            # Corner details
            for angle in [45, 135, 225, 315]:
                x = 20 + int(10 * math.cos(math.radians(angle)))
                y = 20 + int(10 * math.sin(math.radians(angle)))
                pygame.draw.circle(self.image, WHITE, (x, y), 2)
                
        elif self.power_type == "jetpack":
            # Enhanced jetpack with more detail
            # Main body
            pygame.draw.rect(self.image, (120, 120, 120), (14, 8, 12, 20))
            # Fuel tanks
            pygame.draw.rect(self.image, (80, 80, 80), (10, 10, 6, 16))
            pygame.draw.rect(self.image, (80, 80, 80), (24, 10, 6, 16))
            # Central core
            pygame.draw.rect(self.image, RED, (16, 12, 8, 12))
            # Exhaust nozzles
            pygame.draw.rect(self.image, (200, 200, 200), (12, 26, 4, 8))
            pygame.draw.rect(self.image, (200, 200, 200), (24, 26, 4, 8))
            # Flame effects
            flame_points = [(14, 34), (16, 36), (18, 34)]
            pygame.draw.polygon(self.image, ORANGE, flame_points)
            flame_points = [(26, 34), (28, 36), (30, 34)]
            pygame.draw.polygon(self.image, ORANGE, flame_points)
            
        elif self.power_type == "magnet":
            # Enhanced magnet with magnetic field visualization
            # Magnet body
            pygame.draw.rect(self.image, RED, (8, 15, 24, 6))  # Top bar
            pygame.draw.rect(self.image, RED, (8, 21, 24, 6))  # Bottom bar
            pygame.draw.rect(self.image, RED, (8, 15, 6, 12))  # Left side
            pygame.draw.rect(self.image, RED, (26, 15, 6, 12))  # Right side
            # Poles
            pygame.draw.rect(self.image, WHITE, (8, 17, 6, 2))  # N
            pygame.draw.rect(self.image, BLACK, (26, 17, 6, 2))  # S
            # Magnetic field lines
            for radius in [15, 18, 21]:
                pygame.draw.arc(self.image, (100, 100, 255), 
                              (20-radius//2, 20-radius//2, radius, radius), 
                              0, math.pi, 2)
            
        elif self.power_type == "slowtime":
            # Enhanced clock design
            # Clock face
            pygame.draw.circle(self.image, GREEN, (20, 20), 18)
            pygame.draw.circle(self.image, (0, 200, 0), (20, 20), 15)
            pygame.draw.circle(self.image, WHITE, (20, 20), 13, 2)
            pygame.draw.circle(self.image, (200, 255, 200), (20, 20), 10)
            
            # Clock numbers (12, 3, 6, 9)
            font = pygame.font.SysFont("Arial", 8)
            numbers = [(20, 8, "12"), (30, 20, "3"), (20, 30, "6"), (10, 20, "9")]
            for x, y, num in numbers:
                text = font.render(num, True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                self.image.blit(text, text_rect)
            
            # Clock hands
            pygame.draw.line(self.image, BLACK, (20, 20), (20, 10), 3)  # Hour
            pygame.draw.line(self.image, BLACK, (20, 20), (28, 20), 2)  # Minute
            pygame.draw.circle(self.image, BLACK, (20, 20), 3)  # Center
            
            # Time warp effect
            for i in range(3):
                radius = 25 + i * 5
                alpha = 100 - i * 30
                time_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(time_surf, (*GREEN[:3], alpha), (radius, radius), radius, 1)
                time_rect = time_surf.get_rect(center=(20, 20))
                self.image.blit(time_surf, time_rect)
    
    def update(self):
        self.rect.x -= self.speed
        # Floating animation
        self.float_offset += self.float_speed
        self.rect.y = int(self.original_y + math.sin(self.float_offset) * 8)
        
        # Glow animation
        self.glow_phase += 0.1
        
        return self.rect.right < 0
    
    def draw_glow(self, screen):
        # Animated glow effect
        glow_intensity = int(40 + 30 * math.sin(self.glow_phase))
        
        colors = {
            "shield": CYAN,
            "jetpack": ORANGE,
            "magnet": PURPLE,
            "slowtime": GREEN
        }
        
        glow_color = colors.get(self.power_type, WHITE)
        glow_alpha = (*glow_color[:3], glow_intensity)
        
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_alpha, (30, 30), 25)
        glow_rect = glow_surf.get_rect(center=self.rect.center)
        screen.blit(glow_surf, glow_rect)

# Enhanced Game class with all features
class Game:
    def __init__(self):
        self.state = MENU
        self.score = 0
        self.distance = 0
        self.player = Player()
        self.player.game = self
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.particles = []
        self.background_elements = []
        
        # Enhanced game mechanics
        self.speed = 5
        self.current_biome = FOREST
        self.time_of_day = DAY
        self.biome_distance = 0
        self.biome_transition_distance = 1000
        self.obstacle_spawn_timer = 0
        self.coin_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.background_spawn_timer = 0
        
        # Power-up system
        self.active_powerups = {
            "shield": False,
            "jetpack": False,
            "magnet": False,
            "slowtime": False
        }
        self.powerup_timers = {
            "shield": 0,
            "jetpack": 0,
            "magnet": 0,
            "slowtime": 0
        }
        self.powerup_durations = {
            "shield": 300,    # 5 seconds
            "jetpack": 180,   # 3 seconds  
            "magnet": 240,    # 4 seconds
            "slowtime": 180   # 3 seconds
        }
        
        # Mission system
        self.current_mission = None
        self.mission_completed_timer = 0
        self.mission_start_score = 0
        
        # Lives system
        self.lives = 3
        
        # Enhanced effects
        self.screen_shake = 0
        self.time_scale = 1.0
        
        # Load sounds
        self.sounds = load_sounds()
        
        # Background music management
        self.current_music_biome = None
    
    def create_jetpack_particle(self, x, y):
        """Create jetpack exhaust particles"""
        for _ in range(2):
            velocity = (random.uniform(-2, -4), random.uniform(-1, 1))
            color = random.choice([ORANGE, RED, YELLOW])
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity, lifetime))
    
    def activate_powerup(self, power_type):
        """Activate a power-up with enhanced effects"""
        self.active_powerups[power_type] = True
        self.powerup_timers[power_type] = self.powerup_durations[power_type]
        
        # Special activation effects
        if power_type == "jetpack":
            self.player.activate_jetpack(180)  # 3 seconds of fuel
        elif power_type == "slowtime":
            self.time_scale = 0.5
        elif power_type == "magnet":
            # Attract nearby coins
            for coin in self.coins[:]:
                if abs(coin.rect.centerx - self.player.rect.centerx) < 200:
                    # Move coin towards player
                    dx = self.player.rect.centerx - coin.rect.centerx
                    dy = self.player.rect.centery - coin.rect.centery
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0:
                        coin.rect.x += int(dx / distance * 8)
                        coin.rect.y += int(dy / distance * 8)
        
        # Create activation particles
        for _ in range(15):
            colors = {
                "shield": CYAN,
                "jetpack": ORANGE, 
                "magnet": PURPLE,
                "slowtime": GREEN
            }
            color = colors.get(power_type, WHITE)
            velocity = (random.uniform(-3, 3), random.uniform(-5, -2))
            lifetime = random.randint(30, 60)
            self.particles.append(Particle(
                self.player.rect.centerx + random.randint(-20, 20),
                self.player.rect.centery + random.randint(-20, 20),
                color, velocity, lifetime
            ))
    
    def update_powerups(self):
        """Update power-up timers and effects"""
        for power_type in list(self.powerup_timers.keys()):
            if self.powerup_timers[power_type] > 0:
                self.powerup_timers[power_type] -= 1
                
                if self.powerup_timers[power_type] <= 0:
                    self.active_powerups[power_type] = False
                    
                    # Special deactivation effects
                    if power_type == "slowtime":
                        self.time_scale = 1.0
    
    def update_biome(self):
        """Update biome progression with smooth transitions"""
        self.biome_distance += self.speed
        
        if self.biome_distance >= self.biome_transition_distance:
            self.biome_distance = 0
            self.current_biome = (self.current_biome + 1) % 8
            
            # Change time of day every 2 biomes
            if self.current_biome % 2 == 0:
                self.time_of_day = NIGHT if self.time_of_day == DAY else DAY
            
            # Update background music
            if self.current_music_biome != self.current_biome:
                play_biome_music(self.current_biome, self.time_of_day)
                self.current_music_biome = self.current_biome
            
            # Create new mission for new biome
            if not self.current_mission or self.current_mission.completed:
                difficulty = 1.0 + (self.score / 5000)  # Increase difficulty with score
                self.current_mission = Mission(self.current_biome, difficulty)
                self.mission_start_score = self.score
    
    def update_missions(self, coins_collected, player_hit):
        """Update current mission progress"""
        if self.current_mission and self.current_mission.mission_active:
            obstacles_avoided = 0  # Count based on obstacles passed
            for obstacle in self.obstacles:
                if obstacle.rect.right < self.player.rect.left:
                    obstacles_avoided += 1
            
            mission_completed = self.current_mission.update(
                self.current_biome,
                delta_coins=coins_collected,
                delta_obstacles=obstacles_avoided,
                delta_time=1/60,
                player_hit=player_hit,
                current_score=self.score,
                start_score=self.mission_start_score
            )

            
            if mission_completed:
                self.score += self.current_mission.reward
                self.mission_completed_timer = 120  # Show completion message
                
                # Checkpoint system - save progress in new biomes
                if self.current_biome not in biomes_with_checkpoint:
                    global last_checkpoint_x, last_checkpoint_biome
                    last_checkpoint_x = self.distance
                    last_checkpoint_biome = self.current_biome
                    biomes_with_checkpoint.add(self.current_biome)
                    
                    if self.sounds["checkpoint"]:
                        self.sounds["checkpoint"].play()
    
    def spawn_entities(self):
        """Enhanced entity spawning with biome-specific logic"""
        effective_speed = self.speed * self.time_scale
        
        # Spawn obstacles
        self.obstacle_spawn_timer -= 1
        if self.obstacle_spawn_timer <= 0:
            base_interval = 90 - min(40, self.distance // 500)  # Increase difficulty
            spawn_interval = int(base_interval / self.time_scale)
            
            if random.random() > 0.1:  # 90% chance to spawn
                self.obstacles.append(Obstacle(self.current_biome, effective_speed))
            
            self.obstacle_spawn_timer = spawn_interval + random.randint(-20, 20)
        
        # Spawn coins
        self.coin_spawn_timer -= 1
        if self.coin_spawn_timer <= 0:
            if random.random() > 0.3:  # 70% chance
                self.coins.append(Coin(effective_speed))
            
            self.coin_spawn_timer = random.randint(60, 120)
        
        # Spawn power-ups
        self.powerup_spawn_timer -= 1
        if self.powerup_spawn_timer <= 0:
            if random.random() > 0.8:  # 20% chance
                self.powerups.append(PowerUp(effective_speed))
            
            self.powerup_spawn_timer = random.randint(300, 600)
        
        # Spawn background elements
        self.background_spawn_timer -= 1
        if self.background_spawn_timer <= 0:
            if random.random() > 0.4:  # 60% chance
                self.background_elements.append(
                    BackgroundElement(self.current_biome, self.time_of_day, effective_speed)
                )
            
            self.background_spawn_timer = random.randint(30, 90)
    
    def update(self):
        """Main game update loop"""
        if self.state != PLAYING:
            return
        
        # Update biome progression
        self.update_biome()
        
        # Update power-ups
        self.update_powerups()
        
        # Spawn new entities
        self.spawn_entities()
        
        # Update player
        coins_collected, player_hit = self.player.update(self.obstacles, self.coins, self.powerups)
        
        # Update missions
        self.update_missions(coins_collected, player_hit)
        
        # Update score and distance
        self.score += int(1 * self.time_scale)
        self.distance += int(self.speed * self.time_scale)
        
        if coins_collected > 0:
            self.score += coins_collected * 10
        
        # Update entities
        self.obstacles = [obs for obs in self.obstacles if not obs.update()]
        self.coins = [coin for coin in self.coins if not coin.update()]
        self.powerups = [pu for pu in self.powerups if not pu.update()]
        self.background_elements = [bg for bg in self.background_elements if not bg.update()]
        
        # Update particles
        self.particles = [p for p in self.particles if not p.update()]
        
        # Update mission completion timer
        if self.mission_completed_timer > 0:
            self.mission_completed_timer -= 1
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        # Increase game speed gradually
        if self.distance % 1000 == 0 and self.distance > 0:
            self.speed += 0.2
    
    def draw_background(self, screen):
        """Enhanced background rendering with biome-specific details"""
        # Base background color based on biome and time
        background_colors = {
            FOREST: {DAY: SKY_BLUE, NIGHT: (25, 25, 112)},
            SEA: {DAY: (70, 130, 180), NIGHT: (25, 25, 112)},
            SNOW: {DAY: (230, 230, 250), NIGHT: (47, 79, 79)},
            DESERT: {DAY: (255, 218, 185), NIGHT: (72, 61, 139)},
            SKY: {DAY: (135, 206, 235), NIGHT: (25, 25, 112)},
            SPACE: {DAY: SPACE_BLACK, NIGHT: (5, 5, 5)},
            VOLCANO: {DAY: (105, 105, 105), NIGHT: (139, 69, 19)},
            CRYSTAL: {DAY: (221, 160, 221), NIGHT: (72, 61, 139)}
        }
        
        bg_color = background_colors[self.current_biome][self.time_of_day]
        screen.fill(bg_color)
        
        # Add celestial bodies
        if self.time_of_day == DAY:
            # Sun
            sun_x = SCREEN_WIDTH - 150
            sun_y = 80
            pygame.draw.circle(screen, SUN_COLOR, (sun_x, sun_y), 40)
            pygame.draw.circle(screen, YELLOW, (sun_x, sun_y), 35)
            
            # Sun rays
            for angle in range(0, 360, 45):
                ray_end_x = sun_x + int(60 * math.cos(math.radians(angle)))
                ray_end_y = sun_y + int(60 * math.sin(math.radians(angle)))
                pygame.draw.line(screen, SUN_COLOR, (sun_x, sun_y), (ray_end_x, ray_end_y), 3)
        else:
            # Moon and stars
            moon_x = SCREEN_WIDTH - 150
            moon_y = 80
            pygame.draw.circle(screen, MOON_COLOR, (moon_x, moon_y), 35)
            pygame.draw.circle(screen, (200, 200, 200), (moon_x, moon_y), 30)
            
            # Moon craters
            pygame.draw.circle(screen, (180, 180, 180), (moon_x - 10, moon_y - 8), 5)
            pygame.draw.circle(screen, (180, 180, 180), (moon_x + 8, moon_y + 5), 3)
            
            # Stars
            for _ in range(20):
                star_x = random.randint(0, SCREEN_WIDTH)
                star_y = random.randint(0, SCREEN_HEIGHT // 2)
                if random.random() > 0.7:
                    star_size = 2
                    star_color = WHITE
                else:
                    star_size = 1
                    star_color = (200, 200, 200)
                pygame.draw.circle(screen, star_color, (star_x, star_y), star_size)
        
        # Draw background elements (sorted by layer for proper depth)
        back_elements = [bg for bg in self.background_elements if bg.layer == 'back']
        mid_elements = [bg for bg in self.background_elements if bg.layer == 'mid']
        front_elements = [bg for bg in self.background_elements if bg.layer == 'front']
        
        for element in back_elements + mid_elements + front_elements:
            screen.blit(element.image, element.rect)
        
        # Ground
        ground_color = {
            FOREST: FOREST_GREEN,
            SEA: (194, 178, 128),  # Sand
            SNOW: SNOW_WHITE,
            DESERT: (238, 203, 173),
            SKY: (200, 200, 255),
            SPACE: (64, 64, 64),
            VOLCANO: (139, 69, 19),
            CRYSTAL: (138, 43, 226)
        }
        
        ground_rect = (0, GROUND_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_LEVEL)
        pygame.draw.rect(screen, ground_color[self.current_biome], ground_rect)
        
        # Ground texture/details
        if self.current_biome == FOREST:
            # Grass texture
            for x in range(0, SCREEN_WIDTH, 20):
                grass_height = random.randint(5, 15)
                pygame.draw.line(screen, (0, 100, 0), 
                               (x, GROUND_LEVEL), (x, GROUND_LEVEL + grass_height), 2)
        elif self.current_biome == SEA:
            # Wave patterns on shore
            wave_y = GROUND_LEVEL + 10
            for x in range(0, SCREEN_WIDTH, 30):
                wave_height = int(5 * math.sin(x * 0.1))
                pygame.draw.circle(screen, SEA_BLUE, (x, wave_y + wave_height), 8)
        elif self.current_biome == SPACE:
            # Space station lights
            for x in range(50, SCREEN_WIDTH, 100):
                pygame.draw.circle(screen, RED, (x, GROUND_LEVEL + 5), 3)
                pygame.draw.circle(screen, GREEN, (x + 25, GROUND_LEVEL + 5), 3)
    
    def draw_ui(self, screen):
        """Enhanced UI with better visual design"""
        # Semi-transparent UI background
        ui_surf = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(ui_surf, (0, 0, 0, 100), (0, 0, SCREEN_WIDTH, 100))
        screen.blit(ui_surf, (0, 0))
        
        # Score with glow effect
        score_text = font_medium.render(f"Score: {self.score:,}", True, WHITE)
        score_glow = font_medium.render(f"Score: {self.score:,}", True, YELLOW)
        screen.blit(score_glow, (12, 52))
        screen.blit(score_text, (10, 50))
        
        # Distance
        distance_text = font_small.render(f"Distance: {self.distance}m", True, WHITE)
        screen.blit(distance_text, (10, 80))
        
        # Current biome
        biome_text = font_small.render(f"Biome: {biome_names[self.current_biome]}", True, WHITE)
        screen.blit(biome_text, (200, 50))
        
        # Time of day
        time_text = font_small.render(f"Time: {'Day' if self.time_of_day == DAY else 'Night'}", True, WHITE)
        screen.blit(time_text, (200, 70))
        
        # Lives with heart icons
        lives_x = SCREEN_WIDTH - 200
        lives_text = font_small.render("Lives:", True, WHITE)
        screen.blit(lives_text, (lives_x, 50))
        
        for i in range(self.lives):
            heart_x = lives_x + 60 + i * 25
            pygame.draw.polygon(screen, RED, [
                (heart_x, 55), (heart_x - 8, 50), (heart_x - 8, 45),
                (heart_x - 4, 41), (heart_x, 45), (heart_x + 4, 41),
                (heart_x + 8, 45), (heart_x + 8, 50)
            ])
        
        # Active power-ups display
        powerup_y = 10
        active_count = 0
        for power_type, active in self.active_powerups.items():
            if active:
                powerup_x = SCREEN_WIDTH - 250 + active_count * 60
                
                # Power-up icon background
                icon_rect = (powerup_x, powerup_y, 50, 30)
                pygame.draw.rect(screen, (50, 50, 50, 200), icon_rect)
                pygame.draw.rect(screen, WHITE, icon_rect, 2)
                
                # Power-up name
                pu_text = font_small.render(power_type.upper()[:6], True, WHITE)
                text_rect = pu_text.get_rect(center=(powerup_x + 25, powerup_y + 10))
                screen.blit(pu_text, text_rect)
                
                # Timer bar
                timer_progress = self.powerup_timers[power_type] / self.powerup_durations[power_type]
                timer_width = int(46 * timer_progress)
                timer_rect = (powerup_x + 2, powerup_y + 22, timer_width, 6)
                
                colors = {"shield": CYAN, "jetpack": ORANGE, "magnet": PURPLE, "slowtime": GREEN}
                pygame.draw.rect(screen, colors.get(power_type, WHITE), timer_rect)
                
                active_count += 1
        
        # Mission display
        if self.current_mission and self.current_mission.mission_active:
            mission_y = 120
            mission_bg = pygame.Surface((400, 80), pygame.SRCALPHA)
            pygame.draw.rect(mission_bg, (0, 0, 50, 180), (0, 0, 400, 80))
            pygame.draw.rect(mission_bg, WHITE, (0, 0, 400, 80), 2)
            screen.blit(mission_bg, (10, mission_y))
            
            # Mission title
            mission_title = font_small.render("MISSION", True, YELLOW)
            screen.blit(mission_title, (20, mission_y + 10))
            
            # Mission description
            desc_text = font_small.render(self.current_mission.description, True, WHITE)
            screen.blit(desc_text, (20, mission_y + 30))
            
            # Progress bar
            progress = self.current_mission.get_progress_percentage()
            progress_width = int(360 * progress / 100)
            
            progress_bg_rect = (20, mission_y + 50, 360, 15)
            progress_rect = (20, mission_y + 50, progress_width, 15)
            
            pygame.draw.rect(screen, (100, 100, 100), progress_bg_rect)
            pygame.draw.rect(screen, GREEN, progress_rect)
            pygame.draw.rect(screen, WHITE, progress_bg_rect, 2)
            
            # Progress text
            progress_text = font_small.render(f"{progress}% - {self.current_mission.get_progress_text()}", True, WHITE)
            screen.blit(progress_text, (25, mission_y + 52))
        
        # Mission completion notification
        if self.mission_completed_timer > 0:
            alpha = min(255, self.mission_completed_timer * 3)
            completed_surf = pygame.Surface((300, 60), pygame.SRCALPHA)
            pygame.draw.rect(completed_surf, (0, 200, 0, alpha), (0, 0, 300, 60))
            pygame.draw.rect(completed_surf, (255, 255, 255, alpha), (0, 0, 300, 60), 3)
            
            complete_text = font_medium.render("MISSION COMPLETED!", True, (255, 255, 255, alpha))
            reward_text = font_small.render(f"Reward: {self.current_mission.reward} points", True, (255, 255, 255, alpha))
            
            screen.blit(completed_surf, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            screen.blit(complete_text, (SCREEN_WIDTH//2 - complete_text.get_width()//2, SCREEN_HEIGHT//2 - 90))
            screen.blit(reward_text, (SCREEN_WIDTH//2 - reward_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
    
    def draw(self, screen):
        """Main draw function with screen shake effect"""
        # Calculate screen offset for shake effect
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Create temporary surface for shake effect
        if self.screen_shake > 0:
            temp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            temp_surf = screen
        
        # Draw everything
        self.draw_background(temp_surf)
        
        # Draw entities with glow effects
        for coin in self.coins:
            coin.draw_glow(temp_surf)
            temp_surf.blit(coin.image, coin.rect)
        
        for powerup in self.powerups:
            powerup.draw_glow(temp_surf)
            temp_surf.blit(powerup.image, powerup.rect)
        
        for obstacle in self.obstacles:
            temp_surf.blit(obstacle.image, obstacle.rect)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(temp_surf)
        
        # Draw player with effects
        self.player.draw_shield(temp_surf)
        temp_surf.blit(self.player.image, self.player.rect)
        self.player.draw_invulnerability(temp_surf)
        
        # Apply screen shake
        if self.screen_shake > 0:
            screen.blit(temp_surf, (shake_x, shake_y))
        
        # Draw UI (not affected by screen shake)
        self.draw_ui(screen)

def draw_menu(screen):
    """Enhanced main menu with better graphics"""
    # Animated background
    time_factor = pygame.time.get_ticks() * 0.001
    
    # Gradient background
    for y in range(SCREEN_HEIGHT):
        color_ratio = y / SCREEN_HEIGHT
        # Clamp RGB values between 0 and 255
        r = max(0, min(255, int(25 + 30 * math.sin(time_factor + color_ratio))))
        g = max(0, min(255, int(25 + 50 * math.sin(time_factor + color_ratio + 1))))
        b = max(0, min(255, int(112 + 50 * math.sin(time_factor + color_ratio + 2))))
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Animated stars
    for i in range(50):
        star_x = (i * 137) % SCREEN_WIDTH
        star_y = (i * 211) % SCREEN_HEIGHT
        twinkle = math.sin(time_factor * 2 + i) * 0.5 + 0.5
        alpha = int(100 + 155 * twinkle)
        star_color = (*WHITE[:3], alpha)
        
        star_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, star_color, (2, 2), 2)
        screen.blit(star_surf, (star_x, star_y))
    
    # Title with glow effect
    title_glow = font_title.render("COSMIC RUNNER", True, CYAN)
    title_text = font_title.render("COSMIC RUNNER", True, WHITE)
    
    title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    title_y = 100
    
    # Multiple glow layers
    for offset in range(5, 0, -1):
        glow_alpha = 50 - offset * 8
        glow_surf = pygame.Surface(title_glow.get_size(), pygame.SRCALPHA)
        glow_surf.blit(title_glow, (0, 0))
        glow_surf.set_alpha(glow_alpha)
        screen.blit(glow_surf, (title_x - offset, title_y - offset))
    
    screen.blit(title_text, (title_x, title_y))
    
    # Subtitle
    subtitle = font_medium.render("Enhanced Edition", True, YELLOW)
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))
    
    # Menu options with hover effects
    menu_options = [
        ("PLAY", SCREEN_HEIGHT // 2 + 50),
        ("INSTRUCTIONS", SCREEN_HEIGHT // 2 + 100),
        ("QUIT", SCREEN_HEIGHT // 2 + 150)
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    
    for text, y_pos in menu_options:
        option_text = font_large.render(text, True, WHITE)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        
        # Hover effect
        if text_rect.collidepoint(mouse_pos):
            hover_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (255, 255, 255, 30), hover_surf.get_rect())
            screen.blit(hover_surf, (text_rect.x - 10, text_rect.y - 5))
            
            glow_text = font_large.render(text, True, CYAN)
            screen.blit(glow_text, (text_rect.x - 2, text_rect.y - 2))
        
        screen.blit(option_text, text_rect)
    
     # Volume slider with font parameter
    volume_slider.draw(screen, font_small)
    
def draw_instructions(screen):
    """Enhanced instructions screen"""
    # Background
    screen.fill((25, 25, 50))
    
    # Title
    title = font_large.render("HOW TO PLAY", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    # Instructions with better formatting
    instructions = [
        ("CONTROLS:", WHITE, font_medium),
        ("  SPACE - Jump/Jetpack", (200, 200, 200), font_small),
        ("  ESC - Pause Game", (200, 200, 200), font_small),
        ("  F11 - Toggle Fullscreen", (200, 200, 200), font_small),
        ("", WHITE, font_small),
        ("POWER-UPS:", YELLOW, font_medium),
        ("  Shield - Protects from obstacles", CYAN, font_small),
        ("  Jetpack - Fly for limited time", ORANGE, font_small),
        ("  Magnet - Attracts nearby coins", PURPLE, font_small),
        ("  Slow Time - Slows down the game", GREEN, font_small),
        ("", WHITE, font_small),
        ("BIOMES:", GREEN, font_medium),
        ("  Progress through 8 unique biomes", (200, 200, 200), font_small),
        ("  Each biome has day/night cycles", (200, 200, 200), font_small),
        ("  Complete missions for bonus points", (200, 200, 200), font_small),
        ("", WHITE, font_small),
        ("LIVES SYSTEM:", RED, font_medium),
        ("  You have 3 lives", (200, 200, 200), font_small),
        ("  Checkpoints save your progress", (200, 200, 200), font_small),
        ("  Respawn at last checkpoint when you die", (200, 200, 200), font_small),
    ]
    
    y_offset = 120
    for text, color, font_type in instructions:
        if text:
            rendered = font_type.render(text, True, color)
            screen.blit(rendered, (50, y_offset))
        y_offset += 30
    
    # Back instruction
    back_text = font_medium.render("Press ESC to return to menu", True, WHITE)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 80))

def draw_game_over(screen, game):
    """Enhanced game over screen"""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(overlay, (0, 0))
    
    # Game Over title with dramatic effect
    title = font_title.render("GAME OVER", True, RED)
    title_glow = font_title.render("GAME OVER", True, ORANGE)
    
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    title_y = SCREEN_HEIGHT // 2 - 150
    
    # Glowing effect
    for offset in range(3, 0, -1):
        glow_surf = pygame.Surface(title_glow.get_size(), pygame.SRCALPHA)
        glow_surf.blit(title_glow, (0, 0))
        glow_surf.set_alpha(60 - offset * 15)
        screen.blit(glow_surf, (title_x - offset, title_y - offset))
    
    screen.blit(title, (title_x, title_y))
    
    # Stats
    stats = [
        f"Final Score: {game.score:,}",
        f"Distance Traveled: {game.distance:,}m",
        f"Biomes Explored: {game.current_biome + 1}",
        f"Current Biome: {biome_names[game.current_biome]}"
    ]
    
    y_offset = title_y + 100
    for stat in stats:
        stat_text = font_medium.render(stat, True, WHITE)
        screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, y_offset))
        y_offset += 40
    
    # Options
    restart_text = font_large.render("R - Restart", True, GREEN)
    menu_text = font_large.render("M - Main Menu", True, YELLOW)
    quit_text = font_large.render("Q - Quit", True, RED)
    
    option_y = y_offset + 50
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, option_y))
    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, option_y + 50))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, option_y + 100))

def draw_pause_screen(screen, game):
    """Enhanced pause screen"""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 120), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(overlay, (0, 0))
    
    # Pause title
    pause_text = font_title.render("PAUSED", True, CYAN)
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    
    # Current stats
    stats = [
        f"Score: {game.score:,}",
        f"Distance: {game.distance:,}m",
        f"Lives: {game.lives}",
        f"Biome: {biome_names[game.current_biome]}"
    ]
    
    y_offset = SCREEN_HEIGHT // 2 - 20
    for stat in stats:
        stat_text = font_medium.render(stat, True, WHITE)
        screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, y_offset))
        y_offset += 35
    
    # Volume slider with font parameter
    volume_slider.draw(screen, font_small)
    
    # Resume instruction
    resume_text = font_medium.render("Press ESC to resume", True, GREEN)
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT - 100))

def handle_menu_events(event):
    """Handle menu-specific events"""
    global game, lives, last_checkpoint_x, last_checkpoint_biome, biomes_with_checkpoint
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            # Reset game state
            game = Game()
            lives = 3
            last_checkpoint_x = 150
            last_checkpoint_biome = 0
            biomes_with_checkpoint.clear()
            game.state = PLAYING
            play_biome_music(FOREST, DAY)
        elif event.key == pygame.K_i:
            game.state = INSTRUCTIONS
        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            return False
    
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        
        # Check menu option clicks
        menu_options = [
            ("PLAY", SCREEN_HEIGHT // 2 + 50),
            ("INSTRUCTIONS", SCREEN_HEIGHT // 2 + 100),
            ("QUIT", SCREEN_HEIGHT // 2 + 150)
        ]
        
        for i, (text, y_pos) in enumerate(menu_options):
            option_text = font_large.render(text, True, WHITE)
            text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            if text_rect.collidepoint(mouse_pos):
                if i == 0:  # PLAY
                    game = Game()
                    lives = 3
                    last_checkpoint_x = 150
                    last_checkpoint_biome = 0
                    biomes_with_checkpoint.clear()
                    game.state = PLAYING
                    play_biome_music(FOREST, DAY)
                elif i == 1:  # INSTRUCTIONS
                    game.state = INSTRUCTIONS
                elif i == 2:  # QUIT
                    return False
                break
    
    # Handle volume slider
    volume_slider.handle_event(event)
    set_volume(volume_slider.get_volume())
    
    return True

def toggle_fullscreen():
    """Toggle between fullscreen and windowed mode"""
    global screen, is_fullscreen, windowed_size, SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_LEVEL
    
    if is_fullscreen:
        # Switch to windowed
        screen = pygame.display.set_mode(windowed_size)
        SCREEN_WIDTH, SCREEN_HEIGHT = windowed_size
        is_fullscreen = False
    else:
        # Switch to fullscreen
        windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
        is_fullscreen = True
    
    # Update ground level
    GROUND_LEVEL = SCREEN_HEIGHT - REF_GROUND_MARGIN + 75

# Main game loop
def main():
    """Enhanced main game loop"""
    global game
    game = Game()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                
                elif game.state == MENU:
                    if not handle_menu_events(event):
                        running = False
                
                elif game.state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        game.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        game.state = PAUSED
                
                elif game.state == PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        game.state = PLAYING
                
                elif game.state == INSTRUCTIONS:
                    if event.key == pygame.K_ESCAPE:
                        game.state = MENU
                
                elif game.state == GAME_OVER:
                    if event.key == pygame.K_r:
                        # Restart from checkpoint
                        game = Game()
                        game.distance = last_checkpoint_x
                        game.current_biome = last_checkpoint_biome
                        game.player.rect.x = 150
                        game.state = PLAYING
                        play_biome_music(game.current_biome, game.time_of_day)
                    elif event.key == pygame.K_m:
                        game.state = MENU
                        stop_music()
                        pygame.mixer.music.load(os.path.join(bgm_path, "Chills.mp3"))
                        pygame.mixer.music.play(-1, fade_ms=1000)
                        set_volume(volume_slider.get_volume())
                    elif event.key == pygame.K_q:
                        running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == MENU:
                    if not handle_menu_events(event):
                        running = False
                elif game.state == PAUSED:
                    volume_slider.handle_event(event)
                    set_volume(volume_slider.get_volume())
            
            elif event.type == pygame.MOUSEMOTION:
                if game.state == PAUSED:
                    volume_slider.handle_event(event)
        
        # Handle continuous key presses for jetpack
        if game.state == PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and game.active_powerups["jetpack"] and game.player.jetpack_fuel > 0:
                # Continuous jetpack thrust
                pass  # Already handled in player update
        
        # Update game
        if game.state == PLAYING:
            game.update()
        
        # Draw everything
        if game.state == MENU:
            draw_menu(screen)
        elif game.state == INSTRUCTIONS:
            draw_instructions(screen)
        elif game.state == PLAYING:
            game.draw(screen)
        elif game.state == PAUSED:
            game.draw(screen)
            draw_pause_screen(screen, game)
        elif game.state == GAME_OVER:
            game.draw(screen)
            draw_game_over(screen, game)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    stop_music()
    pygame.quit()
    sys.exit()

# Entry point
if __name__ == "__main__":
    main()