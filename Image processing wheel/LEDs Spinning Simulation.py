import pygame
import math

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simulation Example")
clock = pygame.time.Clock()
running = True

class SingleLed():
    def __init__(self, distance: float, theta: float, radius: int): 
        self.distance = distance
        self.angle = theta
        self.color = (255, 255, 255)
        self.center = polar_to_cartesian(distance, theta)
        self.radius = radius

    def change_position(self, distance, theta): 
        self.angle = theta
        self.center = polar_to_cartesian(distance, theta)

    def change_color(self, color): 
        self.color = color

    def update_pixel_color(self, image): 
        x, y = int(self.center[0]), int(self.center[1])
        
        pixels = []

        for i in range(x - self.radius, x + self.radius + 1):
            for j in range(y - self.radius, y + self.radius + 1):
                if ((i - x) ** 2) + ((j - y) ** 2) <= (self.radius ** 2):
                    if 0 <= i < image.get_width() and 0 <= j < image.get_height():
                        pixels.append(image.get_at((i, j)))
        
        if pixels:
            avg_color = tuple(sum(c) // len(pixels) for c in zip(*pixels))
            self.color = avg_color
        else:
            self.color = (0, 0, 0)

    def draw(self): 
        pygame.draw.circle(screen, self.color, self.center, self.radius)

def cartesian_to_polar(x: float, y: float) -> tuple[float, float]: 
    r: float = math.sqrt(x**2 + y**2)
    theta: float = math.atan2(y / x)

    return (r, theta)

def polar_to_cartesian(r: float, theta: float) -> tuple[float, float]: 
    x: float = r * math.cos(theta) + 500
    y: float = r * math.sin(theta) + 500

    return (x, y)

def create_led_strip(amount: int, radius: int, initialAngle: float): 
    strip = []

    for led in range(amount): 
        strip.append(SingleLed(2*led*radius + radius, initialAngle, radius))

    return strip

def create_led_wheel(radii: int, amount: int, radius: int): 
    strips = []

    for strip in range(radii): 
        angle = (2 * math.pi * strip) / radii
        newStrip = create_led_strip(amount, radius, angle)
        strips.append(newStrip)

    return strips

image = pygame.image.load("Space marine green.JPG")

strips = create_led_wheel(40, 120, 2)

speed = 0.1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: 
                speed += 0.01
            if event.key == pygame.K_s: 
                speed -= 0.01

    screen.fill((0, 0, 0))

    for strip in strips: 
        for led in strip: 
            led.update_pixel_color(image)
            led.draw()
            led.change_position(led.distance, led.angle + speed)

    pygame.display.flip()

    clock.tick(144)

pygame.quit()