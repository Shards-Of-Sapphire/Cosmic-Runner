import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 70
PLAYER_SPEED = 6  # Movement speed for free movement

# Game settings
OBSTACLE_SPEED = 5
OBSTACLE_FREQUENCY = 50  # Frames between obstacle spawns
SPEED_INCREASE_RATE = 0.05  # How much to increase speed per score point
COIN_FREQUENCY = 70  # Frames between coin spawns
POWERUP_FREQUENCY = 300  # Frames between powerup spawns

class Player:
    def __init__(self):
        # Start in the middle bottom of the screen
        self.x = WINDOW_WIDTH // 2 - PLAYER_WIDTH // 2
        self.y = WINDOW_HEIGHT - PLAYER_HEIGHT - 30
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.speed = PLAYER_SPEED
        self.shield_active = False
        self.shield_timer = 0
        self.boost_active = False
        self.boost_timer = 0
        
    def move(self, dx, dy):
        # Apply speed boost if active
        if self.boost_active:
            dx *= 1.5
            dy *= 1.5
            
        # Check boundaries for x movement
        if 0 <= self.x + dx <= WINDOW_WIDTH - PLAYER_WIDTH:
            self.x += dx
        
        # Check boundaries for y movement
        if 0 <= self.y + dy <= WINDOW_HEIGHT - PLAYER_HEIGHT:
            self.y += dy
            
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Calculate movement vector
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            
        # Apply movement
        self.move(dx, dy)
        
        # Update powerup timers
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                
        if self.boost_active:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.boost_active = False

    def draw(self, screen):
        # Draw player as a car
        if self.boost_active:
            # Draw boost flames
            flame_points = [
                (self.rect.x + 5, self.rect.y + PLAYER_HEIGHT + 10),
                (self.rect.x + PLAYER_WIDTH//4, self.rect.y + PLAYER_HEIGHT + 20),
                (self.rect.x + PLAYER_WIDTH//2, self.rect.y + PLAYER_HEIGHT + 5)
            ]
            pygame.draw.polygon(screen, (255, 165, 0), flame_points)  # Orange flame
            
            flame_points = [
                (self.rect.x + PLAYER_WIDTH//2, self.rect.y + PLAYER_HEIGHT + 5),
                (self.rect.x + 3*PLAYER_WIDTH//4, self.rect.y + PLAYER_HEIGHT + 20),
                (self.rect.x + PLAYER_WIDTH - 5, self.rect.y + PLAYER_HEIGHT + 10)
            ]
            pygame.draw.polygon(screen, (255, 165, 0), flame_points)  # Orange flame
            
        # Draw car body
        pygame.draw.rect(screen, BLUE, self.rect)
        
        # Add some details
        pygame.draw.rect(screen, BLACK, (self.rect.x + 10, self.rect.y + 10, 30, 20))  # Windows
        pygame.draw.rect(screen, BLACK, (self.rect.x + 5, self.rect.y + PLAYER_HEIGHT - 15, 10, 10))  # Wheel
        pygame.draw.rect(screen, BLACK, (self.rect.x + PLAYER_WIDTH - 15, self.rect.y + PLAYER_HEIGHT - 15, 10, 10))  # Wheel
        
        # Draw headlights
        pygame.draw.circle(screen, (255, 255, 200), (self.rect.x + 10, self.rect.y + 5), 5)
        pygame.draw.circle(screen, (255, 255, 200), (self.rect.x + PLAYER_WIDTH - 10, self.rect.y + 5), 5)
        
        # Draw shield if active
        if self.shield_active:
            pygame.draw.circle(screen, (100, 100, 255, 128), 
                               (self.rect.x + PLAYER_WIDTH//2, self.rect.y + PLAYER_HEIGHT//2), 
                               max(PLAYER_WIDTH, PLAYER_HEIGHT), 2)
            
            # Draw second circle for shield effect
            pygame.draw.circle(screen, (150, 150, 255, 64), 
                               (self.rect.x + PLAYER_WIDTH//2, self.rect.y + PLAYER_HEIGHT//2), 
                               max(PLAYER_WIDTH, PLAYER_HEIGHT) - 5, 1)

class Obstacle:
    def __init__(self, speed):
        self.obstacle_type = random.choice(["car", "rock", "barrel", "spike", "moving", "barrier"])
        self.speed = speed
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.dx = 0  # For moving obstacles
        
        # Configure based on type
        if self.obstacle_type == "car":
            self.width = random.randint(50, 70)
            self.height = random.randint(80, 100)
            self.color = random.choice([RED, (255, 165, 0), (139, 69, 19)])  # Red, Orange, Brown
        elif self.obstacle_type == "rock":
            self.width = random.randint(40, 60)
            self.height = random.randint(40, 60)
            self.color = (100, 100, 100)  # Gray
        elif self.obstacle_type == "barrel":
            self.width = 40
            self.height = 60
            self.color = (139, 69, 19)  # Brown
        elif self.obstacle_type == "spike":
            self.width = 30
            self.height = 50
            self.color = (169, 169, 169)  # Silver
        elif self.obstacle_type == "moving":
            self.width = 50
            self.height = 30
            self.color = PURPLE
            self.dx = random.choice([-3, 3])  # Horizontal movement speed
        elif self.obstacle_type == "barrier":
            self.width = random.randint(200, 400)
            self.height = 20
            self.color = RED
        
        # Random position along the top of the screen
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = -self.height
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.rect.y += self.speed
        
        # Handle moving obstacles
        if self.obstacle_type == "moving":
            self.rect.x += self.dx
            # Bounce off edges
            if self.rect.x <= 0 or self.rect.x + self.width >= WINDOW_WIDTH:
                self.dx *= -1

    def draw(self, screen):
        if self.obstacle_type == "car":
            # Draw car body
            pygame.draw.rect(screen, self.color, self.rect)
            # Windows
            pygame.draw.rect(screen, BLACK, (self.rect.x + 5, self.rect.y + 15, self.width - 10, 20))
            # Wheels
            pygame.draw.rect(screen, BLACK, (self.rect.x - 5, self.rect.y + 20, 10, 15))
            pygame.draw.rect(screen, BLACK, (self.rect.x + self.width - 5, self.rect.y + 20, 10, 15))
            pygame.draw.rect(screen, BLACK, (self.rect.x - 5, self.rect.y + self.height - 25, 10, 15))
            pygame.draw.rect(screen, BLACK, (self.rect.x + self.width - 5, self.rect.y + self.height - 25, 10, 15))
        
        elif self.obstacle_type == "rock":
            # Draw a more natural rock shape
            pygame.draw.ellipse(screen, self.color, self.rect)
            # Add some texture
            for _ in range(5):
                offset_x = random.randint(5, self.width - 10)
                offset_y = random.randint(5, self.height - 10)
                size = random.randint(5, 10)
                pygame.draw.ellipse(screen, (80, 80, 80), 
                                   (self.rect.x + offset_x, self.rect.y + offset_y, size, size))
        
        elif self.obstacle_type == "barrel":
            # Draw barrel body
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw barrel rings
            pygame.draw.rect(screen, BLACK, (self.rect.x, self.rect.y + 10, self.width, 5))
            pygame.draw.rect(screen, BLACK, (self.rect.x, self.rect.y + self.height - 15, self.width, 5))
            # Draw hazard symbol
            pygame.draw.polygon(screen, BLACK, [
                (self.rect.x + self.width//2, self.rect.y + 20),
                (self.rect.x + self.width//2 - 10, self.rect.y + 40),
                (self.rect.x + self.width//2 + 10, self.rect.y + 40)
            ])
        
        elif self.obstacle_type == "spike":
            # Draw spike shape
            pygame.draw.polygon(screen, self.color, [
                (self.rect.x + self.width//2, self.rect.y),  # Top
                (self.rect.x, self.rect.y + self.height),  # Bottom left
                (self.rect.x + self.width, self.rect.y + self.height)  # Bottom right
            ])
            # Add metallic shine
            pygame.draw.line(screen, WHITE, 
                            (self.rect.x + self.width//4, self.rect.y + self.height//4),
                            (self.rect.x + 3*self.width//4, self.rect.y + self.height//4), 2)
        
        elif self.obstacle_type == "moving":
            # Draw a UFO-like moving obstacle
            pygame.draw.ellipse(screen, self.color, self.rect)
            # Draw dome
            pygame.draw.ellipse(screen, CYAN, 
                               (self.rect.x + 10, self.rect.y - 10, self.width - 20, self.height//2))
            # Draw lights
            pygame.draw.circle(screen, (255, 255, 0), 
                              (self.rect.x + 10, self.rect.y + self.height - 10), 5)
            pygame.draw.circle(screen, (255, 255, 0), 
                              (self.rect.x + self.width - 10, self.rect.y + self.height - 10), 5)
        
        elif self.obstacle_type == "barrier":
            # Draw barrier
            pygame.draw.rect(screen, self.color, self.rect)
            # Add striped pattern
            for i in range(0, self.width, 20):
                if i % 40 == 0:  # Alternating pattern
                    pygame.draw.rect(screen, BLACK, 
                                    (self.rect.x + i, self.rect.y, 20, self.height))

class Coin:
    def __init__(self, speed):
        self.width = 20
        self.height = 20
        self.x = random.randint(20, WINDOW_WIDTH - 40)
        self.y = -self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = speed
        self.rotation = 0
        self.value = random.choice([1, 1, 1, 5])  # Mostly 1s with occasional 5s
        self.color = GOLD if self.value == 1 else (200, 130, 0)  # Gold for 1, darker gold for 5
        
    def update(self):
        self.rect.y += self.speed
        self.rotation = (self.rotation + 5) % 360
        
    def draw(self, screen):
        # Calculate ellipse width based on rotation to simulate 3D
        ellipse_width = self.width * abs(math.cos(math.radians(self.rotation))) + 5
        
        # Draw outer coin
        pygame.draw.ellipse(screen, self.color, 
                           (self.rect.x + (self.width - ellipse_width)//2, 
                            self.rect.y, ellipse_width, self.height))
        
        # Draw inner circle
        inner_width = max(ellipse_width - 8, 5)
        pygame.draw.ellipse(screen, (255, 235, 100) if self.value == 1 else (230, 190, 50), 
                           (self.rect.x + (self.width - inner_width)//2, 
                            self.rect.y + 4, inner_width, self.height - 8))
        
        # Draw value
        if ellipse_width > 10:
            font = pygame.font.Font(None, 20)
            text = font.render(str(self.value), True, BLACK)
            screen.blit(text, (self.rect.x + (self.width - text.get_width())//2, 
                             self.rect.y + (self.height - text.get_height())//2))

class Powerup:
    def __init__(self, speed):
        self.width = 30
        self.height = 30
        self.x = random.randint(20, WINDOW_WIDTH - 40)
        self.y = -self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = speed
        self.type = random.choice(["shield", "boost"])
        self.pulse = 0
        
    def update(self):
        self.rect.y += self.speed
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
    def draw(self, screen):
        # Base shape
        pulse_size = int(3 * math.sin(self.pulse))
        
        if self.type == "shield":
            # Shield powerup (blue circle)
            pygame.draw.circle(screen, (0, 100, 255), 
                              (self.rect.x + self.width//2, self.rect.y + self.height//2), 
                              self.width//2 + pulse_size)
            pygame.draw.circle(screen, (100, 200, 255), 
                              (self.rect.x + self.width//2, self.rect.y + self.height//2), 
                              self.width//4)
            
        elif self.type == "boost":
            # Boost powerup (green arrow)
            pygame.draw.circle(screen, GREEN, 
                              (self.rect.x + self.width//2, self.rect.y + self.height//2), 
                              self.width//2 + pulse_size)
            
            # Draw arrow
            arrow_points = [
                (self.rect.x + self.width//2, self.rect.y + 5),  # Top
                (self.rect.x + self.width - 5, self.rect.y + self.height//2),  # Right
                (self.rect.x + 3*self.width//4, self.rect.y + self.height//2),  # Right inner
                (self.rect.x + 3*self.width//4, self.rect.y + self.height - 5),  # Bottom
                (self.rect.x + self.width//4, self.rect.y + self.height - 5),  # Bottom
                (self.rect.x + self.width//4, self.rect.y + self.height//2),  # Left inner
                (self.rect.x + 5, self.rect.y + self.height//2)  # Left
            ]
            pygame.draw.polygon(screen, WHITE, arrow_points)

class Effect:
    def __init__(self, x, y, effect_type):
        self.x = x
        self.y = y
        self.type = effect_type
        self.lifetime = 30  # frames
        self.size = 1
        
    def update(self):
        self.lifetime -= 1
        self.size += 1
        
    def draw(self, screen):
        if self.type == "coin":
            # Coin collection effect
            alpha = int(255 * (self.lifetime / 30))
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (255, 215, 0, alpha), (self.size, self.size), self.size)
            screen.blit(temp_surface, (self.x - self.size, self.y - self.size))
            
        elif self.type == "powerup":
            # Powerup effect
            alpha = int(255 * (self.lifetime / 30))
            temp_surface = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (100, 255, 255, alpha), (self.size * 1.5, self.size * 1.5), self.size * 1.5)
            screen.blit(temp_surface, (self.x - self.size * 1.5, self.y - self.size * 1.5))

class Background:
    def __init__(self):
        self.y = 0
        self.scroll_speed = 5
        # Create a grid of stars in the background
        self.stars = []
        for _ in range(100):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            self.stars.append([x, y, size, color])

    def update(self):
        # Scroll stars
        for star in self.stars:
            star[1] += self.scroll_speed
            if star[1] > WINDOW_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WINDOW_WIDTH)

    def draw(self, screen):
        # Draw dark space background
        screen.fill((20, 20, 40))  # Dark blue/purple space
        
        # Draw stars
        for x, y, size, color in self.stars:
            pygame.draw.circle(screen, color, (x, y), size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Cosmic Runner")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.effects = []
        self.background = Background()
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0
        self.score = 0
        self.coins_collected = 0
        self.current_obstacle_speed = OBSTACLE_SPEED
        self.obstacle_frequency = OBSTACLE_FREQUENCY
        self.coin_frequency = COIN_FREQUENCY
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.distance = 0  # Track distance in game units

    def reset_game(self):
        """Reset the game state for a restart."""
        self.__init__()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()  # Use reset_game method
                if event.key == pygame.K_p:  # Pause game (developer feature)
                    self.pause_game()

        return True
    
    def pause_game(self):
        """Simple pause function"""
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
            
            # Display pause text
            pause_text = self.font.render("PAUSED - Press P to continue", True, WHITE)
            self.screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.flip()
            self.clock.tick(5)  # Slow down while paused

    def update(self):
        if not self.game_over:
            self.background.update()
            self.player.update()
            self.distance += self.current_obstacle_speed / 100  # Update distance traveled
            
            # Spawn obstacles
            self.obstacle_timer += 1
            if self.obstacle_timer >= self.obstacle_frequency:
                self.obstacles.append(Obstacle(self.current_obstacle_speed))
                self.obstacle_timer = 0
                # Gradually decrease spawn time as score increases
                self.obstacle_frequency = max(20, OBSTACLE_FREQUENCY - (self.distance / 100))
            
            # Spawn coins
            self.coin_timer += 1
            if self.coin_timer >= self.coin_frequency:
                self.coins.append(Coin(self.current_obstacle_speed))
                self.coin_timer = 0
            
            # Spawn powerups (less frequently)
            self.powerup_timer += 1
            if self.powerup_timer >= POWERUP_FREQUENCY:
                self.powerups.append(Powerup(self.current_obstacle_speed))
                self.powerup_timer = 0

            # Update obstacles and check collisions
            for obstacle in self.obstacles[:]:
                obstacle.update()
                
                # Check collision with player
                if obstacle.rect.colliderect(self.player.rect):
                    if self.player.shield_active:
                        # Destroy obstacle if shield is active
                        self.obstacles.remove(obstacle)
                        # Flash shield effect
                        self.effects.append(Effect(
                            self.player.rect.x + PLAYER_WIDTH//2, 
                            self.player.rect.y + PLAYER_HEIGHT//2, 
                            "powerup"))
                    else:
                        self.handle_game_over()
                        break
                
                elif obstacle.rect.top > WINDOW_HEIGHT:
                    self.obstacles.remove(obstacle)
                    # Increase obstacle speed as distance increases
                    self.current_obstacle_speed = OBSTACLE_SPEED + (self.distance * SPEED_INCREASE_RATE)
            
            # Update coins and check collection
            for coin in self.coins[:]:
                coin.update()
                
                if coin.rect.colliderect(self.player.rect):
                    self.score += coin.value
                    self.coins_collected += 1
                    self.coins.remove(coin)
                    # Add collection effect
                    self.effects.append(Effect(coin.rect.x + coin.width//2, coin.rect.y + coin.height//2, "coin"))
                    
                elif coin.rect.top > WINDOW_HEIGHT:
                    self.coins.remove(coin)
            
            # Update powerups and check collection
            for powerup in self.powerups[:]:
                powerup.update()
                
                if powerup.rect.colliderect(self.player.rect):
                    if powerup.type == "shield":
                        self.player.shield_active = True
                        self.player.shield_timer = FPS * 5  # 5 seconds of shield
                    elif powerup.type == "boost":
                        self.player.boost_active = True
                        self.player.boost_timer = FPS * 3  # 3 seconds of speed boost
                        
                    self.powerups.remove(powerup)
                    # Add collection effect
                    self.effects.append(Effect(
                        powerup.rect.x + powerup.width//2, 
                        powerup.rect.y + powerup.height//2, 
                        "powerup"))
                    
                elif powerup.rect.top > WINDOW_HEIGHT:
                    self.powerups.remove(powerup)
            
            # Update visual effects
            for effect in self.effects[:]:
                effect.update()
                if effect.lifetime <= 0:
                    self.effects.remove(effect)

    def handle_game_over(self):
        """Handle game over state."""
        self.game_over = True

    def draw(self):
        # Draw background first
        self.background.draw(self.screen)
        
        # Draw game elements
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        for coin in self.coins:
            coin.draw(self.screen)
            
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        for effect in self.effects:
            effect.draw(self.screen)
            
        self.player.draw(self.screen)

        # Draw UI
        # Score and coins
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        coin_text = self.font.render(f"🪙 {self.coins_collected}", True, GOLD)
        self.screen.blit(coin_text, (WINDOW_WIDTH - coin_text.get_width() - 10, 10))
        
        # Distance traveled
        distance_text = self.small_font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        self.screen.blit(distance_text, (10, 50))
        
        # Active powerups
        if self.player.shield_active:
            shield_text = self.small_font.render(f"Shield: {self.player.shield_timer // FPS + 1}s", True, (100, 100, 255))
            self.screen.blit(shield_text, (10, 80))
            
        if self.player.boost_active:
            boost_text = self.small_font.render(f"Boost: {self.player.boost_timer // FPS + 1}s", True, GREEN)
            self.screen.blit(boost_text, (10, 110))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("Game Over!", True, WHITE)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            distance_text = self.font.render(f"Distance: {int(self.distance)}m", True, WHITE)
            coins_text = self.font.render(f"Coins Collected: {self.coins_collected}", True, GOLD)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            self.screen.blit(distance_text, (WINDOW_WIDTH//2 - distance_text.get_width()//2, WINDOW_HEIGHT//2))
            self.screen.blit(coins_text, (WINDOW_WIDTH//2 - coins_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 100))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
