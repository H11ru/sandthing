import random
from data import data

class ParticleSystem:
    def __init__(self, width, height, particle_size, gui_height):
        self.width = width
        self.height = height
        self.particle_size = particle_size
        self.gui_height = gui_height
        
        # Initialize grids
        self.grid_width = width // particle_size
        self.grid_height = (height - gui_height) // particle_size
        self.grid = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        self.life_grid = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        self.ctype_grid = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        
        # Particle tracking
        self.placed = {key: 0 for key in data}
        self.exploded = {key: 0 for key in data}

    def clear_grid(self):
        """Clear all particles from the grid"""
        self.grid = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        self.life_grid = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        self.ctype_grid = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]

    def initialize_particle_life(self, x, y, element):
        """Initialize life value for a particle"""
        if 'slife' in data[element]:
            if isinstance(data[element]['slife'], tuple):
                self.life_grid[x][y] = random.randint(data[element]['slife'][0], data[element]['slife'][1])
            else:
                self.life_grid[x][y] = data[element]['slife']

    def create_particle(self, x, y, element):
        """Create a particle at the given position"""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            old_element = self.grid[x][y]
            self.grid[x][y] = element
            if element:
                self.initialize_particle_life(x, y, element)
                if old_element != element:
                    self.placed[element] += 1
                    if element == "electricity":
                        if old_element in data["electricity"]["conducts"]:
                            self.ctype_grid[x][y] = old_element

    def update_particle_life(self):
        """Update life values for all particles"""
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                element = self.grid[x][y]
                if element and 'slife' in data[element]:
                    self.life_grid[x][y] -= 1
                    if self.life_grid[x][y] <= 0:
                        effect = data[element]['life0'][0]
                        if effect == "die":
                            self.grid[x][y] = None
                        elif effect == "become":
                            new_element = data[element]['life0'][1].lower()
                            self.grid[x][y] = new_element
                            if new_element in data and 'slife' in data[new_element]:
                                self.initialize_particle_life(x, y, new_element)

    def draw(self, screen):
        """Draw all particles"""
        import pygame  # Import here to avoid circular dependency
        
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid[x][y]:
                    element = data[self.grid[x][y]]
                    color = element['color']
                    
                    needs_alpha = False
                    if 'slife' in data[self.grid[x][y]] and data[self.grid[x][y]].get('enablefadingout', True):
                        max_life = data[self.grid[x][y]]['mlife']
                        alpha = int((self.life_grid[x][y] / max_life) * 255)
                        surface = pygame.Surface((self.particle_size, self.particle_size))
                        surface.set_alpha(alpha)
                        surface.fill(color)
                        screen.blit(surface, (x * self.particle_size, y * self.particle_size))
                        needs_alpha = True
                    
                    if not needs_alpha:
                        pygame.draw.rect(screen, color, 
                                      pygame.Rect(x * self.particle_size, 
                                                y * self.particle_size, 
                                                self.particle_size, 
                                                self.particle_size))