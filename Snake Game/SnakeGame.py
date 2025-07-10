import pygame
import sys
import os
from random import randint

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

GRID_WIDTH = 20
GRID_HEIGHT = 20

CELL_WIDTH = SCREEN_WIDTH / GRID_WIDTH
CELL_HEIGHT = SCREEN_HEIGHT / GRID_HEIGHT

DIRECTIONS = {"right": [1 * CELL_WIDTH, 0], 
              "up":    [0, -1 * CELL_HEIGHT], 
              "left":  [-1 * CELL_WIDTH, 0], 
              "down":  [0, 1 * CELL_HEIGHT]}

class BorderBlock(pygame.sprite.Sprite): 
    def __init__(self, x: int, y: int): 
        super().__init__()
        self.image: pygame.Surface = pygame.image.load(resource_path("BorderBlock.png")).convert() 
        self.rect: pygame.Rect = self.image.get_rect(topleft=(x * CELL_WIDTH, y * CELL_HEIGHT))
        
class SnakeSegment(pygame.sprite.Sprite): 
    def __init__(self, x: int = 5, y: int = 5, head: object = None): 
        super().__init__()
        self.pos: tuple[int, int] = (x, y)
        self.prevPos: tuple[int, int] = self.pos
        self.image: pygame.Surface = pygame.image.load(resource_path("SnakeSegment.png")).convert_alpha()
        self.rect: pygame.Rect = self.image.get_rect(topleft=(self.pos[0] * CELL_WIDTH, self.pos[1] * CELL_HEIGHT))
        self.head: SnakeSegment = head
        
        if self.head == None: 
            self.direction: list[int, int] = DIRECTIONS["right"]
            
    def change_direction(self, input: list[int, int]) -> None: 
        if input == DIRECTIONS["right"]: 
            if self.direction != DIRECTIONS["left"]: 
                self.prevDirection = self.direction
                self.direction = DIRECTIONS["right"]
            
        elif input == DIRECTIONS["up"]: 
            if self.direction != DIRECTIONS["down"]: 
                self.prevDirection = self.direction
                self.direction = DIRECTIONS["up"]
            
        elif input == DIRECTIONS["left"]: 
            if self.direction != DIRECTIONS["right"]: 
                self.prevDirection = self.direction
                self.direction = DIRECTIONS["left"]
            
        elif input == DIRECTIONS["down"]: 
            if self.direction != DIRECTIONS["up"]: 
                self.prevDirection = self.direction
                self.direction = DIRECTIONS["down"]
        
    def move(self, first: bool = False) -> None:
        self.prevPos = (self.rect.topleft[0] / CELL_WIDTH, self.rect.topleft[1] / CELL_HEIGHT)
        
        if first: 
            self.rect.move_ip(self.direction[0], self.direction[1])
            
        else: 
            self.rect.move_ip((self.head.prevPos[0] - self.pos[0]) * CELL_WIDTH, (self.head.prevPos[1] - self.pos[1]) * CELL_HEIGHT)
            
        self.pos = (self.rect.topleft[0] / CELL_WIDTH, self.rect.topleft[1] / CELL_HEIGHT)
        
    def update(self, input, rectangle) -> bool: 
        if self.head == None:
            self.change_direction(input)
            self.move(first=True)
            
        else: 
            self.move()
            
        return self.rect.colliderect(rectangle)
        
class Snake(pygame.sprite.Group): 
    def __init__(self, *sprites): 
        super().__init__()
        self.orderedSprites: list = []
        self.add_ordered(*sprites)
        
        self.snakeSpeed: int = 3 # Cells per second
        
        # Create snake timer event
        self.snakeTimer = pygame.event.custom_type()
        self.start_game_timer()
        
    def add_ordered(self, *sprites) -> None: 
        for sprite in sprites: 
            self.orderedSprites.append(sprite)
            self.add(*sprites)
            
    def start_game_timer(self) -> None: 
        pygame.time.set_timer(self.snakeTimer, int((1 / self.snakeSpeed) * 1000))
            
    def stop_game_timer(self) -> None: 
        pygame.time.set_timer(self.snakeTimer, 0)
        
    def get_snake_body_rects(self) -> list: 
        snakeBodyRects = []
        
        for snakeSegment in self.orderedSprites: 
            snakeBodyRects.append(snakeSegment.rect)
            
        return snakeBodyRects
                
    def update(self, *args, **kwargs) -> int: 
        head = self.orderedSprites[0]
        ateApple = head.update(*args, **kwargs)
        
        if ateApple: 
            newSegment = SnakeSegment(head.prevPos[0], head.prevPos[1], head=head)
            self.add(newSegment)
            self.orderedSprites.insert(1, newSegment)
            
            if len(self.orderedSprites) >= 3: 
                self.orderedSprites[2].head = newSegment
            
            return 1
            
        else: 
            for i in range(len(self.orderedSprites) - 1): 
                self.orderedSprites[i + 1].update(*args, **kwargs)
                
            return 0

class Apple(pygame.sprite.Sprite): 
    def __init__(self, snakeBody): 
        super().__init__()
        self.image: pygame.Surface = pygame.image.load(resource_path("Apple.png")).convert_alpha()
        self.rect: pygame.Rect = self.image.get_rect(topleft = (-1 * CELL_WIDTH, -1 * CELL_HEIGHT))
        self.new_apple_pos(snakeBody)
        
    def new_apple_pos(self, snakeBody: list[pygame.Rect]) -> None: 
        pos: tuple[int, int] = (randint(1, GRID_WIDTH - 2) * CELL_WIDTH, randint(1, GRID_HEIGHT - 2) * CELL_HEIGHT)

        self.rect.topleft = pos
        
        if self.rect.collidelist(snakeBody) >= 0: 
            return self.new_apple_pos(snakeBody)
        
    def update(self, snakeBody: list[pygame.Rect]) -> None: 
        if self.rect.collidelist(snakeBody) >= 0: 
            self.new_apple_pos(snakeBody)
        
def resource_path(relative_path):
    """ Get the absolute path to a resource, works for both development and PyInstaller's onefile mode """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as an executable, the base path is the script location
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_border(group: pygame.sprite.Group): 
    for y in range(GRID_HEIGHT): 
        for x in range(GRID_WIDTH): 
            if y == 0 or y == (GRID_HEIGHT - 1): 
                group.add(BorderBlock(x, y))
            else: 
                if x == 0 or x == (GRID_WIDTH - 1): 
                    group.add(BorderBlock(x, y))

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ssssssnake")
clock = pygame.time.Clock()

# Create borders with sprites
borderBlocks = pygame.sprite.Group()
create_border(borderBlocks)
                
# Create snake with sprites
snake = Snake(SnakeSegment())

# Create apple with sprites
apple = pygame.sprite.GroupSingle(Apple(snake.get_snake_body_rects()))

# Create Game Over scene
textFont = pygame.font.Font(resource_path("RedHatDisplay-Regular.ttf"), 30)
gameOverTextSurf = textFont.render("Game Over", False, "darkgreen")
gameOverTextRect = gameOverTextSurf.get_rect(midtop = (SCREEN_WIDTH / 2, 75))

restartTextSurf = textFont.render("Press SPACE to restart", False, "darkgreen")
restartTextRect = restartTextSurf.get_rect(midtop = (SCREEN_WIDTH / 2, 350))

gameOverImageSurf1 = pygame.image.load(resource_path("GameOverImage.png")).convert_alpha()
gameOverImageRect1 = gameOverImageSurf1.get_rect(midtop = (SCREEN_WIDTH / 2 - 12, 200))

gameOverImageSurf2 = pygame.image.load(resource_path("Apple.png")).convert_alpha()
gameOverImageRect2 = gameOverImageSurf2.get_rect(midleft = gameOverImageRect1.midright)

# Game States
running = True
gameOver = False

# Game score
gameScore = 0

while running: 
    if gameOver:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE: 
                    # Change game state and restart score
                    gameOver = False
                    gameScore = 0
                    input = DIRECTIONS["right"]
                    
                    # Restart sprites
                    snake.add_ordered(SnakeSegment())
                    apple.add(Apple(snake.get_snake_body_rects()))
                    create_border(borderBlocks)
                    
                    # Restart snake movement timer
                    snake.start_game_timer()
                    
        # Create Game Over scene
        screen.fill("chartreuse3")
        screen.blit(gameOverTextSurf, gameOverTextRect)
        screen.blit(restartTextSurf, restartTextRect)
        screen.blit(gameOverImageSurf1, gameOverImageRect1)
        screen.blit(gameOverImageSurf2, gameOverImageRect2)
        
        gameScoreTextSurf = textFont.render(f"Total score: {gameScore}", False, "darkgreen")
        gameScoreTextRect = gameScoreTextSurf.get_rect(midtop = (SCREEN_WIDTH / 2, 400))
        
        screen.blit(gameScoreTextSurf, gameScoreTextRect)
        
    else:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_d: 
                    input = DIRECTIONS["right"]
                elif event.key == pygame.K_w: 
                    input = DIRECTIONS["up"]
                elif event.key == pygame.K_a: 
                    input = DIRECTIONS["left"]
                elif event.key == pygame.K_s: 
                    input = DIRECTIONS["down"]
                
            if event.type == snake.snakeTimer:
                gameScore += snake.update(input, apple.sprite.rect)
                apple.update(snake.get_snake_body_rects())
                
        if pygame.sprite.spritecollideany(snake.orderedSprites[0], borderBlocks) or pygame.sprite.spritecollideany(snake.orderedSprites[0], snake.orderedSprites[1:]): 
            # Change game state
            gameOver = True
            
            # Reset sprites
            snake.empty()
            snake.orderedSprites = []
            apple.empty()
            borderBlocks.empty()
            
            # Reset snake movement timer
            snake.stop_game_timer()
        
        # Paint background green
        screen.fill("chartreuse3")
            
        # Draw border blocks
        borderBlocks.draw(screen)
        
        # Draw apple
        apple.draw(screen)
        
        # Draw Snake 
        snake.draw(screen)
        
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()