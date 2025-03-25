import random
import pygame
from data import data
from rigid_body import RigidBody
from explosion_manager import ExplosionManager

class PhysicsEngine:
    def __init__(self, particle_system):
        self.particle_system = particle_system
        self.explosion_manager = ExplosionManager()
        self.rigid_bodies = []
        
    def update(self):
        """Update physics for both particles and rigid bodies"""
        self.update_particles()
        self.update_rigid_bodies()
        
    def update_particles(self):
        """Update particle physics including interactions"""
        self.particle_system.update_particle_life()
        
        # Update in random order for more natural behavior
        positions = [(x, y) for x in range(self.particle_system.grid_width) 
                    for y in range(self.particle_system.grid_height) 
                    if self.particle_system.grid[x][y] is not None]
        random.shuffle(positions)
        
        for x, y in positions:
            tile = self.particle_system.grid[x][y]
            if not tile:
                continue
                
            # Handle particle interactions
            self._handle_particle_interactions(x, y, tile)
            
            # Handle particle movement
            self._handle_particle_movement(x, y, tile)
    
    def _handle_particle_interactions(self, x, y, tile):
        """Handle interactions between particles"""
        # Water + Lava interaction
        if tile == "water":
            self._check_water_interactions(x, y)
            
        # Handle transmutations
        if data[tile].get('transmuteonpresence', False):
            self._handle_transmutation(x, y, tile)
            
        # Handle electricity
        if tile == "electricity":
            self._handle_electricity(x, y)
            
        # Handle ice melting
        if tile == "ice":
            self._handle_ice_melting(x, y)
            
        # Handle fire spread
        if data[tile].get('flaming', False):
            self._check_fire_spread(x, y, tile)
            
        # Handle plant growth
        if tile == "plant":
            self._check_plant_growth(x, y)
            
        # Handle corrosion
        if data[tile].get('corrode', False):
            self._check_corrosion(x, y, tile)
            
        # Handle cloning
        if data[tile].get('clone', False):
            self._check_cloning(x, y, tile)

    def _check_water_interactions(self, x, y):
        """Handle water interactions with other particles"""
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height):
                adjacent_tile = self.particle_system.grid[nx][ny]
                
                # Water + Lava interaction
                if adjacent_tile == "lava":
                    self.particle_system.grid[x][y] = "steam"
                    self.particle_system.initialize_particle_life(x, y, "steam")
                    self.particle_system.grid[nx][ny] = "obsidian"
                    self.particle_system.initialize_particle_life(nx, ny, "obsidian")
                    continue
                
                # Water + Salt interaction
                elif adjacent_tile == "salt":
                    self.particle_system.grid[nx][ny] = None
                    continue

    def _handle_transmutation(self, x, y, tile):
        """Handle particle transmutation"""
        things = data[tile]['transmuteonpresence'][0]
        if not isinstance(things, list):
            things = [things]
        becomes = data[tile]['transmuteonpresence'][1]
        
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height):
                if self.particle_system.grid[nx][ny] in things:
                    self.particle_system.grid[x][y] = becomes
                    self.particle_system.initialize_particle_life(x, y, becomes)
                    break

    def _handle_electricity(self, x, y):
        """Handle electricity behavior"""
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height):
                if (self.particle_system.grid[nx][ny] in data["electricity"]["conducts"] and
                    self.particle_system.life_grid[nx][ny] <= 0):
                    self.particle_system.ctype_grid[nx][ny] = self.particle_system.grid[nx][ny]
                    self.particle_system.grid[nx][ny] = "electricity"
                    self.particle_system.life_grid[nx][ny] = 2

    def _handle_ice_melting(self, x, y):
        """Handle ice melting near heat sources"""
        import random
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height and
                self.particle_system.grid[nx][ny] in ["fire", "lava"]):
                if random.random() < 0.2:  # 20% chance per frame
                    self.particle_system.grid[x][y] = "water"
                    break

    def _check_fire_spread(self, x, y, tile):
        """Handle fire spreading to flammable materials"""
        import random
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height and
                self.particle_system.grid[nx][ny] is not None):
                target_tile = self.particle_system.grid[nx][ny]
                if data[target_tile].get('flammable', False):
                    if random.random() < data[tile].get('burn', 0.01) * data[target_tile].get('burnm', 0.01):
                        if data[target_tile].get('exploderad', False):
                            self._handle_explosion(nx, ny, data[target_tile]['exploderad'])
                        else:
                            new_tile = tile
                            if data[target_tile].get('overrideburn', False):
                                new_tile = data[target_tile]['overrideburn']
                            elif data[tile].get('overridemyburn', False):
                                new_tile = data[tile]['overridemyburn']
                            self.particle_system.grid[nx][ny] = new_tile
                            self.particle_system.initialize_particle_life(nx, ny, new_tile)

    def _check_plant_growth(self, x, y):
        """Handle plant growth"""
        import random
        if y > 0 and self.particle_system.grid[x][y-1] is None:
            has_water = False
            water_pos = None
            
            for dx, dy in [(-1,0), (1,0), (0,1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.particle_system.grid_width and
                    0 <= ny < self.particle_system.grid_height and
                    self.particle_system.grid[nx][ny] == "water"):
                    has_water = True
                    water_pos = (nx, ny)
                    break
            
            if not has_water:
                if random.random() < 0.001:
                    self.particle_system.grid[x][y-1] = "plant"
                    self.particle_system.initialize_particle_life(x, y-1, "plant")
            elif water_pos:
                self.particle_system.grid[water_pos[0]][water_pos[1]] = None
                self.particle_system.grid[x][y-1] = "plant"
                self.particle_system.initialize_particle_life(x, y-1, "plant")

    def _check_corrosion(self, x, y, tile):
        """Handle corrosion effects"""
        import random
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height and
                self.particle_system.grid[nx][ny] is not None):
                if self.particle_system.grid[nx][ny] not in data[tile]['excludecorrode']:
                    if random.random() < 0.1:
                        self.particle_system.grid[nx][ny] = None
                    elif random.random() < 0.01:
                        self.particle_system.grid[x][y] = None

    def _check_cloning(self, x, y, tile):
        """Handle cloning behavior"""
        import random
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height and
                self.particle_system.grid[nx][ny] is None):
                growth_chance = 0.05 if tile == "plant" else 0.8
                if random.random() < growth_chance:
                    if tile == "plant" and (dy <= 0 or random.random() < 0.3):
                        new_tile = data[tile]['clone']
                        self.particle_system.grid[nx][ny] = new_tile
                        self.particle_system.initialize_particle_life(nx, ny, new_tile)
                    elif tile != "plant":
                        new_tile = data[tile]['clone']
                        self.particle_system.grid[nx][ny] = new_tile
                        self.particle_system.initialize_particle_life(nx, ny, new_tile)

    def _handle_explosion(self, x, y, radius):
        """Handle particle explosion effects"""
        import random
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.particle_system.grid_width and
                        0 <= ny < self.particle_system.grid_height):
                        current_tile = self.particle_system.grid[nx][ny]
                        if current_tile and data[current_tile].get('shatter'):
                            self.particle_system.exploded[current_tile] += 1
                            shattered_type = data[current_tile]['shatter']
                            self.particle_system.grid[nx][ny] = shattered_type
                            if shattered_type in data and 'slife' in data[shattered_type]:
                                self.particle_system.initialize_particle_life(nx, ny, shattered_type)
                        elif (random.random() < 0.1 and current_tile not in
                              ["wall", "fire", "lava", "electricity", "steam", "obsidian"]):
                            self.particle_system.grid[nx][ny] = "fire"
                            self.particle_system.initialize_particle_life(nx, ny, "fire")

    def _handle_particle_movement(self, x, y, tile):
        """Handle particle movement based on fall type"""
        if 'fall' not in data[tile]:
            return
            
        fall_type = data[tile]['fall']
        density = data[tile].get('density', 1)
        
        if fall_type == 0:  # Solid
            return
            
        elif fall_type == 1:  # Powder
            self._handle_powder_movement(x, y, density)
            
        elif fall_type == 2:  # Liquid
            self._handle_liquid_movement(x, y, density)
            
        elif fall_type == -1:  # Rising (fire)
            self._handle_rising_movement(x, y, density)
            
        elif fall_type == 3:  # Gas
            self._handle_gas_movement(x, y, density)

    def _handle_powder_movement(self, x, y, density):
        """Handle powder-like particle movement"""
        # Check below first
        if y + 1 < self.particle_system.grid_height:
            if (self.particle_system.grid[x][y + 1] is None or
                (self.particle_system.grid[x][y + 1] and
                 data[self.particle_system.grid[x][y + 1]].get('density', 1) < density)):
                self._swap_particles(x, y, x, y + 1)
                return
            
            # Check down-left and down-right in random order
            import random
            for dx in random.sample([-1, 1], 2):
                nx, ny = x + dx, y + 1
                if (0 <= nx < self.particle_system.grid_width and
                    (self.particle_system.grid[nx][ny] is None or
                     (self.particle_system.grid[nx][ny] and
                      data[self.particle_system.grid[nx][ny]].get('density', 1) < density))):
                    self._swap_particles(x, y, nx, ny)
                    return

    def _handle_liquid_movement(self, x, y, density):
        """Handle liquid particle movement"""
        import random
        # Check below first
        if y + 1 < self.particle_system.grid_height:
            if (self.particle_system.grid[x][y + 1] is None or
                (self.particle_system.grid[x][y + 1] and
                 data[self.particle_system.grid[x][y + 1]].get('density', 1) < density)):
                self._swap_particles(x, y, x, y + 1)
                return
            
            # Check diagonal down
            for dx in random.sample([-1, 1], 2):
                nx, ny = x + dx, y + 1
                if (0 <= nx < self.particle_system.grid_width and
                    (self.particle_system.grid[nx][ny] is None or
                     (self.particle_system.grid[nx][ny] and
                      data[self.particle_system.grid[nx][ny]].get('density', 1) < density))):
                    self._swap_particles(x, y, nx, ny)
                    return
        
        # Try to spread horizontally
        for dx in random.sample([-1, 1], 2):
            nx = x + dx
            if (0 <= nx < self.particle_system.grid_width and
                (self.particle_system.grid[nx][y] is None or
                 (self.particle_system.grid[nx][y] and
                  data[self.particle_system.grid[nx][y]].get('density', 1) < density))):
                self._swap_particles(x, y, nx, y)
                return

    def _handle_rising_movement(self, x, y, density):
        """Handle rising particle movement (e.g., fire)"""
        import random
        # Check above first
        if y > 0:
            if (self.particle_system.grid[x][y - 1] is None or
                (self.particle_system.grid[x][y - 1] and
                 data[self.particle_system.grid[x][y - 1]].get('density', 1) < density)):
                self._swap_particles(x, y, x, y - 1)
                return
            
            # Check diagonal up
            for dx in random.sample([-1, 1], 2):
                nx, ny = x + dx, y - 1
                if (0 <= nx < self.particle_system.grid_width and
                    (self.particle_system.grid[nx][ny] is None or
                     (self.particle_system.grid[nx][ny] and
                      data[self.particle_system.grid[nx][ny]].get('density', 1) < density))):
                    self._swap_particles(x, y, nx, ny)
                    return

    def _handle_gas_movement(self, x, y, density):
        """Handle gas particle movement"""
        import random
        # Pick a random direction in 3x3 area
        directions = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx != 0 or dy != 0]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.particle_system.grid_width and
                0 <= ny < self.particle_system.grid_height and
                (self.particle_system.grid[nx][ny] is None or
                 (self.particle_system.grid[nx][ny] and
                  data[self.particle_system.grid[nx][ny]].get('density', 1) < density))):
                self._swap_particles(x, y, nx, ny)
                return

    def _swap_particles(self, x1, y1, x2, y2):
        """Swap two particles and their associated properties"""
        # Swap grid contents
        self.particle_system.grid[x1][y1], self.particle_system.grid[x2][y2] = \
            self.particle_system.grid[x2][y2], self.particle_system.grid[x1][y1]
        
        # Swap life values
        self.particle_system.life_grid[x1][y1], self.particle_system.life_grid[x2][y2] = \
            self.particle_system.life_grid[x2][y2], self.particle_system.life_grid[x1][y1]
        
        # Swap ctype values
        self.particle_system.ctype_grid[x1][y1], self.particle_system.ctype_grid[x2][y2] = \
            self.particle_system.ctype_grid[x2][y2], self.particle_system.ctype_grid[x1][y1]

    def update_rigid_bodies(self):
        """Update physics for all rigid bodies"""
        dt = 1/60  # Fixed timestep
        
        for body in self.rigid_bodies:
            body.update(dt)
            
            # Check collisions with particles
            world_cells = body.get_world_cells()
            for cell_x, cell_y in world_cells:
                if (0 <= cell_x < self.particle_system.grid_width and 
                    0 <= cell_y < self.particle_system.grid_height):
                    if (self.particle_system.grid[cell_x][cell_y] and 
                        body.material["pushes_particles"]):
                        # Displace particle based on rigid body movement
                        self._handle_particle_displacement(cell_x, cell_y, body)
            
            # Apply boundary constraints
            self._constrain_rigid_body(body)

    def _constrain_rigid_body(self, body):
        """Keep rigid body within bounds and handle collisions"""
        world_cells = body.get_world_cells()
        for cell_x, cell_y in world_cells:
            if cell_x < 0:
                body.x -= cell_x
                body.velocity[0] *= -0.5  # Bounce
            elif cell_x >= self.particle_system.grid_width:
                body.x -= (cell_x - self.particle_system.grid_width + 1)
                body.velocity[0] *= -0.5
                
            if cell_y < 0:
                body.y -= cell_y
                body.velocity[1] *= -0.5
            elif cell_y >= self.particle_system.grid_height:
                body.y -= (cell_y - self.particle_system.grid_height + 1)
                body.velocity[1] *= -0.5

    def _handle_particle_displacement(self, x, y, body):
        """Handle displacement of particles by rigid bodies"""
        dx = -1 if body.velocity[0] < 0 else 1
        dy = -1 if body.velocity[1] < 0 else 1
        
        # Try to move particle to adjacent empty space
        for offset_x, offset_y in [(dx,0), (0,dy), (dx,dy), (-dx,0), (0,-dy)]:
            new_x, new_y = x + offset_x, y + offset_y
            if (0 <= new_x < self.particle_system.grid_width and 
                0 <= new_y < self.particle_system.grid_height and 
                self.particle_system.grid[new_x][new_y] is None):
                # Move particle
                self.particle_system.grid[new_x][new_y] = self.particle_system.grid[x][y]
                self.particle_system.grid[x][y] = None
                return

    def create_explosion(self, x, y, radius):
        """Create an explosion affecting both particles and rigid bodies"""
        # Handle rigid body physics
        self.explosion_manager.handle_explosion(x, y, radius, self.rigid_bodies)
        
        # Handle particle effects
        self.explosion_manager.create_particle_explosion(x, y, radius, 
                                                       self.particle_system.grid,
                                                       self.particle_system)

    def draw(self, screen):
        """Draw all rigid bodies"""
        for body in self.rigid_bodies:
            body.draw(screen, self.particle_system.particle_size)