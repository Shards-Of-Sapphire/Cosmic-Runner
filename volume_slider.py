import pygame

class VolumeSlider:
    def __init__(self, x, y, width, height=10, knob_radius=10, initial_volume=0.5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.knob_radius = knob_radius

        self.volume = initial_volume
        self.knob_x = self.x + int(self.volume * self.width)
        self.knob_y = self.y + self.height // 2

        self.knob_rect = pygame.Rect(0, 0, knob_radius*2, knob_radius*2)
        self.knob_rect.center = (self.knob_x, self.knob_y)

        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.x, min(event.pos[0], self.x + self.width))
            self.knob_x = new_x
            self.knob_rect.centerx = self.knob_x

            relative_x = self.knob_x - self.x
            self.volume = relative_x / self.width
            pygame.music.set_volume(self.volume)

    def draw(self, surface, font):
        # Draw background bar
        pygame.draw.rect(surface, (180, 180, 180), (self.x, self.y, self.width, self.height))

        # Draw filled part
        fill_width = int(self.volume * self.width)
        pygame.draw.rect(surface, (100, 200, 255), (self.x, self.y, fill_width, self.height))

        # Draw knob
        pygame.draw.circle(surface, (255, 255, 255), (self.knob_x, self.knob_y), self.knob_radius)

        # Draw volume text
        volume_percent = int(self.volume * 100)
        text = font.render(f"Volume: {volume_percent}%", True, (255, 255, 255))
        surface.blit(text, (self.x + self.width + 20, self.y - 10))

    def get_volume(self):
        return self.volume
