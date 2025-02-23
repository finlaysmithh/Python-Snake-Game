import os
import pygame
import random
import sys  # To exit the game properly

# =================== CONFIGURATION ===================
MOVE_INTERVAL = 140         # Logical move interval (ms per grid cell); lower = faster snake.
RENDER_FPS = 50             # Frames per second for rendering.
ROTATION_SPEED = 1650       # Head rotation speed (degrees per second).
BORDER_WIDTH = 2            # Thickness of the tight white outline.
# =================== END CONFIGURATION ===================

# Set working directory
os.chdir("/Users/finlaysmith/Documents/snake/")
print("Working Directory:", os.getcwd())

# Load persistent high score if available
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
else:
    high_score = 0

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions and cell size
WIDTH, HEIGHT = 1000, 800
CELL_SIZE = 50

# Colors
BLUE = (0, 33, 165)
LIGHT_BLUE = (30, 120, 240)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chelsea Themed Snake Game - Outlined")

def draw_background():
    """Draw a checkered background with alternating blue shades."""
    for x in range(0, WIDTH, CELL_SIZE):
        for y in range(0, HEIGHT, CELL_SIZE):
            color = BLUE if ((x // CELL_SIZE + y // CELL_SIZE) % 2 == 0) else LIGHT_BLUE
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

def draw_with_outline(surface, image, pos, outline_color, border_width):
    """
    Draws an image at pos with a tight outline around its non-transparent pixels.
    The outline is computed from the image's mask.
    """
    mask = pygame.mask.from_surface(image)
    outline = mask.outline()
    if len(outline) >= 2:
        outline = [(p[0] + pos[0], p[1] + pos[1]) for p in outline]
        pygame.draw.lines(surface, outline_color, True, outline, border_width)
    surface.blit(image, pos)

# Load background music
bg_music = "Blue_is_the_color_chelsea_Toks_E_Naijapals (online-audio-converter.com).wav"
try:
    pygame.mixer.music.load(bg_music)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print("Error loading background music:", e)

# Load Chelsea logo
try:
    chelsea_logo = pygame.image.load("chelsea_logo.jpeg").convert_alpha()
    chelsea_logo = pygame.transform.scale(chelsea_logo, (120, 120))
except pygame.error as e:
    print("Error loading Chelsea logo:", e)
    chelsea_logo = None

# Load football (food)
try:
    football = pygame.image.load("football.png").convert_alpha()
    football.set_colorkey(WHITE)
    football = pygame.transform.scale(football, (CELL_SIZE, CELL_SIZE))
except pygame.error as e:
    print("Error loading football image:", e)
    sys.exit()

# Load Cole Palmer image (snake head)
try:
    cole_palmer_head = pygame.image.load("cole_palmer.png").convert_alpha()
    cole_palmer_head = pygame.transform.scale(cole_palmer_head, (CELL_SIZE, CELL_SIZE))
except pygame.error as e:
    print("Error loading Cole Palmer image:", e)
    sys.exit()

# Load snake body texture and scale it to 1.5 times CELL_SIZE
try:
    snake_body_img = pygame.image.load("snake_body.png").convert_alpha()
    new_body_size = int(CELL_SIZE * 1.5)
    snake_body_img = pygame.transform.scale(snake_body_img, (new_body_size, new_body_size))
except pygame.error as e:
    print("Error loading snake body texture:", e)
    sys.exit()

# Load sounds
try:
    goal_sound = pygame.mixer.Sound("goal_sound.wav")
except pygame.error as e:
    print("Error loading goal sound:", e)
    sys.exit()

try:
    game_over_sound = pygame.mixer.Sound("game_over.wav")
except pygame.error as e:
    print("Error loading game over sound:", e)
    sys.exit()

def quit_game():
    pygame.quit()
    sys.exit()

def angle_for_direction(direction):
    if direction == RIGHT:
        return -90
    elif direction == LEFT:
        return 90
    elif direction == UP:
        return 0
    elif direction == DOWN:
        return 180

def show_start_screen():
    pygame.mixer.music.play(-1)
    draw_background()
    if chelsea_logo:
        screen.blit(chelsea_logo, (WIDTH - 140, 20))
    font = pygame.font.Font(None, 80)
    title_text = font.render("CHELSEA THEMED SNAKE GAME", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
    font_small = pygame.font.Font(None, 50)
    instructions = font_small.render("Press SPACE to Start | ESC to Quit", True, WHITE)
    screen.blit(instructions, instructions.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def show_game_over():
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(game_over_sound)
    draw_background()
    if chelsea_logo:
        screen.blit(chelsea_logo, (WIDTH - 140, 20))
    font = pygame.font.Font(None, 100)
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    font_small = pygame.font.Font(None, 50)
    instructions = font_small.render("Press SPACE to Restart | ESC to Quit", True, WHITE)
    screen.blit(instructions, instructions.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def run_game():
    global snake, score, high_score
    # Initialize snake with float positions for smooth interpolation.
    snake = [(300.0, 300.0), (250.0, 300.0), (200.0, 300.0)]
    snake_dir = RIGHT
    current_dir = RIGHT  # Update instantly on key press.
    head_angle = angle_for_direction(RIGHT)
    food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
    score = 0
    last_move_time = pygame.time.get_ticks()
    prev_snake = list(snake)
    clock = pygame.time.Clock()
    
    while True:
        dt_frame = clock.tick(RENDER_FPS)
        current_time = pygame.time.get_ticks()
        dt_grid = current_time - last_move_time
        t = dt_grid / MOVE_INTERVAL
        if t > 1:
            t = 1
        
        draw_background()
        if chelsea_logo:
            screen.blit(chelsea_logo, (WIDTH - 140, 20))
        
        # Process input: allow turning only if it isn’t a direct 180° reversal.
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_dir != DOWN:
                    current_dir = UP
                elif event.key == pygame.K_DOWN and snake_dir != UP:
                    current_dir = DOWN
                elif event.key == pygame.K_LEFT and snake_dir != RIGHT:
                    current_dir = LEFT
                elif event.key == pygame.K_RIGHT and snake_dir != LEFT:
                    current_dir = RIGHT
        
        # Determine target angle from current_dir.
        target_angle = angle_for_direction(current_dir)
        diff = target_angle - head_angle
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        max_change = ROTATION_SPEED * dt_frame / 1000.0
        if abs(diff) < max_change:
            head_angle = target_angle
        else:
            head_angle += max_change if diff > 0 else -max_change
        
        # Update snake's logical position if enough time has passed.
        if dt_grid >= MOVE_INTERVAL:
            last_move_time = current_time
            prev_snake = list(snake)
            snake_dir = current_dir
            head_x, head_y = snake[0]
            new_head = (head_x + snake_dir[0] * CELL_SIZE, head_y + snake_dir[1] * CELL_SIZE)
            if (new_head in snake or new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT):
                show_game_over()
                return
            snake.insert(0, new_head)
            if new_head == food:
                pygame.mixer.Sound.play(goal_sound)
                food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                        random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
                score += 1
                if score > high_score:
                    high_score = score
                    with open("highscore.txt", "w") as f:
                        f.write(str(high_score))
            else:
                snake.pop()
            t = 0
        
        # Interpolate positions for smooth rendering.
        interpolated_snake = []
        for i in range(len(snake)):
            if i < len(prev_snake):
                prev_x, prev_y = prev_snake[i]
            else:
                prev_x, prev_y = snake[i]
            curr_x, curr_y = snake[i]
            interp_x = prev_x + (curr_x - prev_x) * t
            interp_y = prev_y + (curr_y - prev_y) * t
            interpolated_snake.append((interp_x, interp_y))
        
        # Draw head using interpolated position and updated head_angle.
        head_pos = interpolated_snake[0]
        rotated_head = pygame.transform.rotate(cole_palmer_head, head_angle)
        draw_with_outline(screen, rotated_head, (int(head_pos[0]), int(head_pos[1])), WHITE, BORDER_WIDTH)
        
        # Draw body segments using interpolated positions.
        for pos in interpolated_snake[1:]:
            draw_x = int(pos[0] + CELL_SIZE // 2 - new_body_size // 2)
            draw_y = int(pos[1] + CELL_SIZE // 2 - new_body_size // 2)
            draw_with_outline(screen, snake_body_img, (draw_x, draw_y), WHITE, BORDER_WIDTH)
        
        screen.blit(football, (food[0], food[1]))
        font = pygame.font.Font(None, 40)
        score_text = font.render(f"Goals: {score}   Most Goals: {high_score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        pygame.display.flip()

while True:
    show_start_screen()
    run_game()
