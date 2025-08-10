import pygame
import os

# Initialize mixer
pygame.mixer.init()

# Get current directory
current_dir = os.path.dirname(__file__)

# Biome constants (matching main game)
FOREST = 0
SEA = 1
SNOW = 2
SKY = 3
SPACE = 4

# Biome music files
BIOME_MUSIC = {
    FOREST: os.path.join(current_dir, "assets", "music", "On.mp3"),
    SEA: os.path.join(current_dir, "assets", "music", "All Over.mp3"),
    SNOW: os.path.join(current_dir, "assets", "music", "Dusted.mp3"),
    SKY: os.path.join(current_dir, "assets", "music", "Glory.mp3"),
    SPACE: os.path.join(current_dir, "assets", "music", "Galaxial.mp3")
}

# Track current biome and volume
current_biome_playing = None
current_volume = 1.0  # Range: 0.0 (mute) to 1.0 (full volume)

def play_biome_music(biome, fade_duration_ms=1000):
    """Play music for the specified biome with crossfade"""
    global current_biome_playing

    if biome == current_biome_playing:
        return

    pygame.mixer.music.fadeout(fade_duration_ms)

    music_path = BIOME_MUSIC.get(biome)
    if music_path:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(current_volume)
        pygame.mixer.music.play(-1, fade_ms=fade_duration_ms)
        current_biome_playing = biome

def stop_music(fade_duration_ms=1000):
    """Stop the currently playing music with fade out"""
    global current_biome_playing
    pygame.mixer.music.fadeout(fade_duration_ms)
    current_biome_playing = None

def set_volume(volume):
    """Set the volume of the music
    Args:
        volume (float): Volume level between 0.0 and 1.0
    """
    global current_volume
    current_volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
    pygame.mixer.music.set_volume(volume)