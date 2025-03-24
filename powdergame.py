import pygame
from data import data, achievements  # Import achievements from data
import random  # For random order logic

# Constants
WIDTH, HEIGHT = 800, 480  # Increased height for the board area
PARTICLE_SIZE = 5  # Reduced particle size for better fit
GUI_HEIGHT = 40
ACHIEVEMENT_DISPLAY_TIME = 3  # Seconds to display achievement notification
FPS = 60  # Added FPS constant for consistent timing
NORMAL_BRUSH_SIZE = 1  # Normal brush size (1 particle)
LARGE_BRUSH_SIZE = 5   # Larger brush size when holding shift (5 particle radius)

# Achievement tracking
active_achievements = []  # List of currently displaying achievements
achievement_timer = 0     # Timer for achievement display
achievement_font = None   # Font for achievement text
achievement_counts = {}   # Track counts for achievement conditions
placed = {}
for key in data:
    placed[key] = 0  # Initialize placed counts for each particle type

# Bresenham's Line Algorithm
def bresenham(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Selection GUI setup
buttons = []
for index, (key, value) in enumerate(data.items()):
    button_rect = pygame.Rect(index * (WIDTH // len(data)), HEIGHT - GUI_HEIGHT, WIDTH // len(data), GUI_HEIGHT)
    buttons.append((button_rect, value['label'], value["color"]))

# Initialize grid
grid = [[None for _ in range((HEIGHT - GUI_HEIGHT) // PARTICLE_SIZE)] for _ in range(WIDTH // PARTICLE_SIZE)]  # Initialize grid
life_grid = [[0 for _ in range((HEIGHT - GUI_HEIGHT) // PARTICLE_SIZE)] for _ in range(WIDTH // PARTICLE_SIZE)]  # Store life values
last_mouse_pos = None  # Track the last mouse position
selected_element = None

# Simulation state
simulation_running = False  # Initial state of simulation (paused)

def initialize_particle_life(x, y, element):
    if 'slife' in data[element]:
        if isinstance(data[element]['slife'], tuple):
            # Random value between the range
            grid_life = random.randint(data[element]['slife'][0], data[element]['slife'][1])
        else:
            grid_life = data[element]['slife']
        life_grid[x][y] = grid_life

def update_particle_life():
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            element = grid[x][y]
            if element and 'slife' in data[element]:
                life_grid[x][y] -= 1
                if life_grid[x][y] <= 0:
                    # Handle life0 effect
                    effect = data[element]['life0'][0]
                    if effect == "die":
                        grid[x][y] = None
                        # Track achievement progress
                        if element not in achievement_counts:
                            achievement_counts[element] = 0
                        achievement_counts[element] += 1
                    elif effect == "become":
                        new_element = data[element]['life0'][1].lower()
                        grid[x][y] = new_element
                        # Initialize new life if the new element has life
                        if new_element in data and 'slife' in data[new_element]:
                            initialize_particle_life(x, y, new_element)
                        # Track achievement progress for the original element
                        if element not in achievement_counts:
                            achievement_counts[element] = 0
                        achievement_counts[element] += 1

# Sand falling logic
def fall_sand():
    # new feature: update in random order instead of top to down
    positions = [(x, y) for x in range(len(grid)) for y in range(len(grid[0])) if grid[x][y] is not None]
    random.shuffle(positions)  # Shuffle positions for random order
    for x, y in positions:
        tile = grid[x][y]
        if tile:
            # Check for exploding items
            # water + lava = water becomes steam, lava becomes obsidian
            if tile == "water":
                # Check all 8 adjacent tiles
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 
                        grid[nx][ny] == "lava"):
                        # Convert water to steam
                        grid[x][y] = "steam"
                        # Initialize life for steam
                        initialize_particle_life(x, y, "steam")
                        # Convert lava to obsidian
                        grid[nx][ny] = "obsidian"
                        # Initialize life for obsidian
                        initialize_particle_life(nx, ny, "obsidian")
                        continue

            # Check for flaming stuff (like fire) spreading to flammable materials
            if data[tile].get('flaming', False):
                # Check all 8 adjacent tiles
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 
                        grid[nx][ny] is not None and 
                        data[grid[nx][ny]].get('flammable', False)):
                        # burn * burnm chance to set fire to it. (get burn from flaming, burnm from burning)
                        if random.random() < data[tile].get('burn', 0.01) * data[grid[nx][ny]].get('burnm', 0.01):
                            # dynamite?
                            if data[grid[nx][ny]].get('exploderad', False):
                                # 
                                if True:
                                    radius = data[grid[nx][ny]]['exploderad']
                                    # Create explosion in radius
                                    for dx2222 in range(-radius, radius + 1):
                                        for dy2222 in range(-radius, radius + 1):
                                            if dx2222*dx2222 + dy2222*dy2222 <= radius*radius:  # Circular explosion
                                                nx2, ny2 = nx + dx2222, ny + dy2222
                                                if 0 <= nx2 < len(grid) and 0 <= ny2 < len(grid[0]):
                                                    # Check if target can shatter
                                                    if grid[nx2][ny2] and data[grid[nx2][ny2]].get('shatter'):
                                                        # Convert to shattered form
                                                        shattered_type = data[grid[nx2][ny2]]['shatter']
                                                        grid[nx2][ny2] = shattered_type
                                                        # Initialize life if needed
                                                        if shattered_type in data and 'slife' in data[shattered_type]:
                                                            initialize_particle_life(nx2, ny2, shattered_type)
                                                    else:
                                                        pass
                                    # Remove the exploded dynamite by fire
                                    grid[nx][ny] = "lava" if random.random() < 0.2 else "fire"
                                    # initialize life for fire
                                    if grid[nx][ny] in data and 'slife' in data[grid[nx][ny]]:
                                        initialize_particle_life(nx, ny, grid[nx][ny])
                                    continue ### STUUUUUUUUU
                            else:
                                # Check overrideburn of the target tile, not the source tile
                                target_tile = grid[nx][ny]
                                new_tile = tile if not data[target_tile].get('overrideburn', False) else data[target_tile]['overrideburn']
                                if data[tile].get('overridemyburn', False) and not data[target_tile].get('overrideburn', False):
                                    # Check if the target tile has a different overrideburn
                                    new_tile = data[tile]['overridemyburn']
                                # Set the new tile and initialize its life
                                grid[nx][ny] = new_tile
                                # Initialize new life if the new element has life
                                initialize_particle_life(nx, ny, new_tile)

            # acidic
            if data[tile].get('corrode', False):
                # Check all 8 adjacent tiles
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 
                        grid[nx][ny] is not None):  # Removed the corrode check here
                        # Check if the target tile is not in our excludecorrode tuple
                        if grid[nx][ny] not in data[tile]['excludecorrode']:
                            # Corrode the target tile
                            if random.random() < 0.1:
                                # Corrode it
                                grid[nx][ny] = None
                                # Track achievement progress for the original element
                                if tile not in achievement_counts:
                                    achievement_counts[tile] = 0
                                achievement_counts[tile] += 1
                            else:
                                # chance for acid to also disappear over time, acid isn't infinite
                                if random.random() < 0.01:
                                    grid[x][y] = None

            # clone
            if data[tile].get('clone', False):
                # Check all 8 adjacent tiles
                for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 
                        grid[nx][ny] is None):  # Only clone to empty spaces
                        # clone the value of clone to this
                        new_tile = data[tile]['clone']
                        grid[nx][ny] = new_tile
                        # Initialize new life if the new element has life
                        if new_tile in data and 'slife' in data[new_tile]:
                            initialize_particle_life(nx, ny, new_tile)

            # Regular falling logic continues...
            if 'fall' in data[tile]:
                fall_type = data[tile]['fall']
                density = data[tile].get('density', 1)
                
                if fall_type == 0:
                    continue  # Solid, no movement
                
                if fall_type == 1:  # Powder fall
                    # Check below first
                    if y + 1 < len(grid[0]) and (grid[x][y + 1] is None or (grid[x][y + 1] and data[grid[x][y + 1]].get('density', 1) < density)):
                        grid[x][y + 1], grid[x][y] = grid[x][y], grid[x][y + 1]
                        life_grid[x][y + 1], life_grid[x][y] = life_grid[x][y], life_grid[x][y + 1]
                        continue
                    
                    # Check down-left and down-right in random order
                    for dx, dy in random.sample([(1, 1), (-1, 1)], 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (grid[nx][ny] is None or (grid[nx][ny] and data[grid[nx][ny]].get('density', 1) < density)):
                            grid[nx][ny], grid[x][y] = grid[x][y], grid[nx][ny]
                            life_grid[nx][ny], life_grid[x][y] = life_grid[x][y], life_grid[nx][ny]
                            continue

                elif fall_type == 2:  # Liquid fall
                    # Check below first
                    if y + 1 < len(grid[0]) and (grid[x][y + 1] is None or (grid[x][y + 1] and data[grid[x][y + 1]].get('density', 1) < density)):
                        grid[x][y + 1], grid[x][y] = grid[x][y], grid[x][y + 1]
                        life_grid[x][y + 1], life_grid[x][y] = life_grid[x][y], life_grid[x][y + 1]
                        continue
                    
                    # Check down-left and down-right in random order
                    for dx, dy in random.sample([(1, 1), (-1, 1)], 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (grid[nx][ny] is None or (grid[nx][ny] and data[grid[nx][ny]].get('density', 1) < density)):
                            grid[nx][ny], grid[x][y] = grid[x][y], grid[nx][ny]
                            life_grid[nx][ny], life_grid[x][y] = life_grid[x][y], life_grid[nx][ny]
                            continue
                    
                    # Check left and right in random order
                    for dx, dy in random.sample([(-1, 0), (1, 0)], 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (grid[nx][ny] is None or (grid[nx][ny] and data[grid[nx][ny]].get('density', 1) < density)):
                            grid[nx][ny], grid[x][y] = grid[x][y], grid[nx][ny]
                            life_grid[nx][ny], life_grid[x][y] = life_grid[x][y], life_grid[nx][ny]
                            continue

                elif fall_type == -1:  # Up fall (fire)
                    # Check above first
                    if y - 1 >= 0 and (grid[x][y - 1] is None or (grid[x][y - 1] and data[grid[x][y - 1]].get('density', 1) < density)):
                        grid[x][y - 1], grid[x][y] = grid[x][y], grid[x][y - 1]
                        life_grid[x][y - 1], life_grid[x][y] = life_grid[x][y], life_grid[x][y - 1]
                        continue
                    
                    # Check up-left and up-right in random order
                    for dx, dy in random.sample([(-1, -1), (1, -1)], 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (grid[nx][ny] is None or (grid[nx][ny] and data[grid[nx][ny]].get('density', 1) < density)):
                            grid[nx][ny], grid[x][y] = grid[x][y], grid[nx][ny]
                            life_grid[nx][ny], life_grid[x][y] = life_grid[x][y], life_grid[nx][ny]
                            continue

                elif fall_type == 3:  # Gas
                    # Pick a random adjacent tile (3x3 box, diagonals allowed)
                    random_neighbors = random.sample(
                        [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)], 8
                    )
                    for dx, dy in random_neighbors:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (grid[nx][ny] is None or (grid[nx][ny] and data[grid[nx][ny]].get('density', 1) < density)):
                            grid[nx][ny], grid[x][y] = grid[x][y], grid[nx][ny]
                            life_grid[nx][ny], life_grid[x][y] = life_grid[x][y], life_grid[nx][ny]
                            continue

                else:
                    print("Error: Unknown fall type")
                    quit()

def check_achievements():
    for achievement_id, achievement in achievements.items():
        if not achievement['achieved']:
            if achievement['type'] in ['Achievement', 'Challenge', 'SECRET']:
                condition = achievement['condit'][0]
                
                if condition == 'liferanout':
                    # Count how many particles of the specified type have run out of life
                    particle_type = achievement['condit'][1]
                    required_amount = int(achievement['condit'][2])
                    
                    if particle_type not in achievement_counts:
                        achievement_counts[particle_type] = 0
                    
                    if achievement_counts[particle_type] >= required_amount:
                        unlock_achievement(achievement_id)
                
                elif condition == 'place':
                    # Check for particle placement achievements
                    particle_type = achievement['condit'][1]
                    if len(achievement['condit']) > 2:
                        required_amount = int(achievement['condit'][2])
                        if particle_type == '*':
                            # Any particle type counts
                            if sum(list(placed.values())) >= required_amount:
                                unlock_achievement(achievement_id)
                        else:
                            # Specific particle type
                            if placed[particle_type] >= required_amount:
                                unlock_achievement(achievement_id)
                    else:
                        # Check if any particle has been placed
                        if placed[particle_type] > 0:
                            unlock_achievement(achievement_id)
                
                elif condition == 'place1ofall':
                    # Check if player has placed at least one of each particle type
                    if all(placed[key] > 0 for key in data.keys()):
                        unlock_achievement(achievement_id)

def unlock_achievement(achievement_id):
    if not achievements[achievement_id]['achieved']:
        achievements[achievement_id]['achieved'] = True
        active_achievements.append({
            'name': achievements[achievement_id]['name'],
            'description': achievements[achievement_id]['description'],
            'time': ACHIEVEMENT_DISPLAY_TIME,
            'type': achievements[achievement_id]['type'],
        })

def update_achievements(dt):
    global active_achievements
    # Remove expired achievements
    new_achievements = []
    for ach in active_achievements:
        ach['time'] -= 1/FPS
        if ach['time'] > 0:
            new_achievements.append(ach)
    active_achievements = new_achievements

def draw_achievements(screen):
    global achievement_font
    if not achievement_font:
        achievement_font = pygame.font.Font(None, 32)
    
    y_offset = 10
    for achievement in active_achievements:
        # Draw achievement notification
        text = f"{achievement['type']} Completed: {achievement['name']}"
        subtext = f"{achievement['description']}"
        text_surface = achievement_font.render(text, True, (255, 215, 0))  # Gold color
        subtext_surface = achievement_font.render(subtext, True, (255, 255, 255))
        
        # Calculate width based on both text surfaces
        width = max(text_surface.get_width(), subtext_surface.get_width())
        
        # Create background surface with alpha
        padding = 10
        bg_height = text_surface.get_height() + subtext_surface.get_height() + padding * 2
        bg_surface = pygame.Surface((width + padding * 2, bg_height))
        bg_surface.fill((0, 0, 0))
        bg_surface.set_alpha(128)
        
        # Position everything
        bg_rect = pygame.Rect(10, y_offset, width + padding * 2, bg_height)
        text_pos = (bg_rect.x + padding, bg_rect.y + padding)
        subtext_pos = (bg_rect.x + padding, bg_rect.y + padding + text_surface.get_height())
        
        # Draw everything
        screen.blit(bg_surface, bg_rect)
        screen.blit(text_surface, text_pos)
        screen.blit(subtext_surface, subtext_pos)
        
        y_offset += bg_height + 5

def draw_with_brush(grid_x, grid_y, element, brush_size):
    global placed
    for dx in range(-brush_size + 1, brush_size):
        for dy in range(-brush_size + 1, brush_size):
            # Calculate distance from center to create circular brush
            if dx*dx + dy*dy <= brush_size*brush_size:
                new_x, new_y = grid_x + dx, grid_y + dy
                if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):
                    old_element = grid[new_x][new_y]
                    grid[new_x][new_y] = element
                    if element:
                        initialize_particle_life(new_x, new_y, element)
                        # Only count if we're placing on an empty space or replacing a different element
                        if old_element != element:
                            placed[element] += 1
                            

# Main loop
running = True
last_mouse_pressed = (False, False, False)  # Track the last mouse button state
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                simulation_running = not simulation_running
            elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Clear the board when Ctrl+F is pressed
                grid = [[None for _ in range((HEIGHT - GUI_HEIGHT) // PARTICLE_SIZE)] for _ in range(WIDTH // PARTICLE_SIZE)]
                life_grid = [[0 for _ in range((HEIGHT - GUI_HEIGHT) // PARTICLE_SIZE)] for _ in range(WIDTH // PARTICLE_SIZE)]

    # Handle key events for simulation toggle
    keys = pygame.key.get_pressed()
    shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    brush_size = LARGE_BRUSH_SIZE if shift_held else NORMAL_BRUSH_SIZE

    # Handle mouse input
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    # Check for button clicks (left click only)
    if mouse_y >= HEIGHT - GUI_HEIGHT:  # Only process button clicks in GUI area
        for button_rect, label, _ in buttons:
            if button_rect.collidepoint(mouse_x, mouse_y):
                if mouse_pressed[0]:  # Left click to select
                    selected_element = next(key for key, value in data.items() if value['label'] == label)

    # Drawing elements with left click or erasing with right click
    grid_x = mouse_x // PARTICLE_SIZE
    grid_y = mouse_y // PARTICLE_SIZE

    if 0 <= grid_x < len(grid) and 0 <= grid_y < len(grid[0]):
        if mouse_pressed[0] and selected_element:  # Left click to draw
            if not last_mouse_pressed[0]:  # Mouse button just pressed
                last_mouse_pos = None
            # Draw a line from the last position to the current position
            if last_mouse_pos:
                last_grid_x, last_grid_y = last_mouse_pos
                line_points = bresenham(last_grid_x, last_grid_y, grid_x, grid_y)
                for px, py in line_points:
                    if 0 <= px < len(grid) and 0 <= py < len(grid[0]):
                        draw_with_brush(px, py, selected_element, brush_size)
            else:
                draw_with_brush(grid_x, grid_y, selected_element, brush_size)
            last_mouse_pos = (grid_x, grid_y)
        elif mouse_pressed[2]:  # Right click to erase
            if not last_mouse_pressed[2]:  # Mouse button just pressed
                last_mouse_pos = None
            if last_mouse_pos:
                last_grid_x, last_grid_y = last_mouse_pos
                line_points = bresenham(last_grid_x, last_grid_y, grid_x, grid_y)
                for px, py in line_points:
                    if 0 <= px < len(grid) and 0 <= py < len(grid[0]):
                        draw_with_brush(px, py, None, brush_size)
            else:
                draw_with_brush(grid_x, grid_y, None, brush_size)
            last_mouse_pos = (grid_x, grid_y)
        elif not any(mouse_pressed):  # No mouse buttons pressed
            last_mouse_pos = None
            
    # Store current mouse state for next frame
    last_mouse_pressed = mouse_pressed

    # Update grid when simulation is running
    if simulation_running:
        update_particle_life()  # Update life values before falling logic
        fall_sand()  # Apply sand falling logic

    # Always update and check achievements
    update_achievements(1/FPS)
    check_achievements()

    # Draw everything
    screen.fill((255, 255, 255))
    
    # Draw particles
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y]:
                element = data[grid[x][y]]
                color = element['color']
                
                brr = 1  # Flag to check if we need to draw no alpha
                # If element has life, adjust alpha based on remaining life
                if 'slife' in data[grid[x][y]]:
                    if data[grid[x][y]].get('enablefadingout', True):
                        max_life = data[grid[x][y]]['mlife']
                        alpha = int((life_grid[x][y] / max_life) * 255)
                        surface = pygame.Surface((PARTICLE_SIZE, PARTICLE_SIZE))
                        surface.set_alpha(alpha)
                        surface.fill(color)
                        screen.blit(surface, (x * PARTICLE_SIZE, y * PARTICLE_SIZE))
                        brr = 0
                    
                if brr: pygame.draw.rect(screen, color, pygame.Rect(x * PARTICLE_SIZE, y * PARTICLE_SIZE, PARTICLE_SIZE, PARTICLE_SIZE))

    # Draw GUI
    for button_rect, label, color in buttons:
        pygame.draw.rect(screen, color, button_rect)
        font = pygame.font.Font(None, 24)
        text = font.render(label, True, (0, 0, 0))
        # CeNTERED
        screen.blit(text, (button_rect.x + (button_rect.width - text.get_width()) // 2, button_rect.y + (button_rect.height - text.get_height()) // 2))

    # Draw achievements if any exist
    if active_achievements:
        draw_achievements(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
