import pygame
from data import data, map_labels_to_items
from rigid_body import RigidBody

class UIManager:
    def __init__(self, width, height, gui_height, particle_size):
        self.width = width
        self.height = height
        self.gui_height = gui_height
        self.particle_size = particle_size
        
        # UI state
        self.selected_element = None
        self.last_mouse_pos = None
        self.brush_size = 1
        self.large_brush_size = 5
        
        # Rigid body state
        self.rigid_body_mode = False
        self.selected_shape = "box"
        self.selected_material = "wood_block"
        self.selected_rigid_body = None
        self.shapes = ["box", "ball", "beam", "triangle"]
        self.materials = ["wood_block", "metal_block", "rubber", "crystal"]
        
        # Initialize buttons
        self.buttons = self._create_buttons()
        
    def _create_buttons(self):
        """Create particle selection buttons"""
        buttons = []
        total_items = len(data.items())
        items_per_row = (total_items + 1) // 2
        button_height = self.gui_height // 2
        
        for index, (key, value) in enumerate(data.items()):
            row = index // items_per_row
            col = index % items_per_row
            
            button_width = self.width // items_per_row
            button_x = col * button_width
            button_y = self.height - self.gui_height + (row * button_height)
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            buttons.append((button_rect, value['label'], value["color"]))
        
        return buttons
    
    def _bresenham(self, x1, y1, x2, y2):
        """Bresenham's Line Algorithm"""
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
    
    def handle_event(self, event, particle_system, physics_engine):
        """Handle UI events"""
        if event.type == pygame.KEYDOWN:
            self._handle_key_press(event, physics_engine)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event, particle_system, physics_engine)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.last_mouse_pos = None
            if event.button == 1 and self.selected_rigid_body:  # Release selected rigid body
                self.selected_rigid_body.selected = False
                self.selected_rigid_body = None
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event, particle_system, physics_engine)
            
        # Handle brush size with shift key
        keys = pygame.key.get_pressed()
        self.brush_size = self.large_brush_size if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1

    def _handle_key_press(self, event, physics_engine):
        """Handle keyboard controls"""
        if event.key == pygame.K_TAB:
            # Toggle between particle and rigid body mode
            self.rigid_body_mode = not self.rigid_body_mode
        elif self.rigid_body_mode:
            if event.key == pygame.K_1:  # Shape selection
                self.selected_shape = self.shapes[(self.shapes.index(self.selected_shape) + 1) % len(self.shapes)]
            elif event.key == pygame.K_2:  # Material selection
                self.selected_material = self.materials[(self.materials.index(self.selected_material) + 1) % len(self.materials)]
            elif event.key == pygame.K_g and self.selected_rigid_body:  # Toggle gravity
                self.selected_rigid_body.gravity_enabled = not self.selected_rigid_body.gravity_enabled
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT) and self.selected_rigid_body:  # Rotation
                direction = 1 if event.key == pygame.K_RIGHT else -1
                self.selected_rigid_body.angular_velocity += direction * 2.0
            elif event.key == pygame.K_DELETE and self.selected_rigid_body:  # Delete rigid body
                physics_engine.rigid_bodies.remove(self.selected_rigid_body)
                self.selected_rigid_body = None

    def _handle_mouse_down(self, event, particle_system, physics_engine):
        """Handle mouse button press events"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check for button clicks in GUI area
        if mouse_y >= self.height - self.gui_height:
            if event.button == 1:  # Left click
                for button_rect, label, _ in self.buttons:
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_element = next(key for key, value in data.items()
                                                  if value['label'] == label)
                        self.rigid_body_mode = False  # Switch back to particle mode
                        break
        else:
            grid_x = mouse_x // self.particle_size
            grid_y = mouse_y // self.particle_size
            
            if event.button == 1:  # Left click
                if self.rigid_body_mode:
                    # Check if clicked on existing rigid body
                    for body in physics_engine.rigid_bodies:
                        world_cells = body.get_world_cells()
                        if (grid_x, grid_y) in world_cells:
                            self.selected_rigid_body = body
                            body.selected = True
                            break
                    else:  # Not clicked on existing body, create new one
                        new_body = RigidBody(self.selected_shape, self.selected_material, grid_x, grid_y)
                        physics_engine.rigid_bodies.append(new_body)
        
    def _handle_mouse_motion(self, event, particle_system, physics_engine):
        """Handle mouse movement events"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        if mouse_y < self.height - self.gui_height:  # Only handle in non-GUI area
            grid_x = mouse_x // self.particle_size
            grid_y = mouse_y // self.particle_size
            
            if self.rigid_body_mode and self.selected_rigid_body and mouse_buttons[0]:
                # Move selected rigid body
                dx = (grid_x - self.last_mouse_pos[0]) if self.last_mouse_pos else 0
                dy = (grid_y - self.last_mouse_pos[1]) if self.last_mouse_pos else 0
                
                self.selected_rigid_body.x += dx
                self.selected_rigid_body.y += dy
                
                # Reset velocity when dragging
                self.selected_rigid_body.velocity = [0, 0]
                self.selected_rigid_body.angular_velocity = 0
            elif not self.rigid_body_mode:
                if mouse_buttons[0] and self.selected_element:  # Left click to draw
                    self._draw_line(grid_x, grid_y, particle_system, self.selected_element)
                elif mouse_buttons[2]:  # Right click to erase
                    self._draw_line(grid_x, grid_y, particle_system, None)
            
            self.last_mouse_pos = (grid_x, grid_y)
    
    def _draw_line(self, grid_x, grid_y, particle_system, element):
        """Draw a line of particles between last position and current position"""
        if self.last_mouse_pos:
            last_grid_x, last_grid_y = self.last_mouse_pos
            line_points = self._bresenham(last_grid_x, last_grid_y, grid_x, grid_y)
            for px, py in line_points:
                self._draw_with_brush(px, py, particle_system, element)
        else:
            self._draw_with_brush(grid_x, grid_y, particle_system, element)
        
        self.last_mouse_pos = (grid_x, grid_y)
    
    def _draw_with_brush(self, grid_x, grid_y, particle_system, element):
        """Draw particles in a brush pattern around the given position"""
        for dx in range(-self.brush_size + 1, self.brush_size):
            for dy in range(-self.brush_size + 1, self.brush_size):
                if dx*dx + dy*dy <= self.brush_size*self.brush_size:
                    particle_system.create_particle(grid_x + dx, grid_y + dy, element)
    
    def draw(self, screen):
        """Draw UI elements"""
        # Draw particle buttons in particle mode
        if not self.rigid_body_mode:
            for button_rect, label, color in self.buttons:
                pygame.draw.rect(screen, color, button_rect)
                font = pygame.font.Font(None, 24)
                text_color = (255, 255, 255) if data[map_labels_to_items[label]].get("textiswhite", False) else (0, 0, 0)
                text = font.render(label, True, text_color)
                screen.blit(text, (button_rect.x + (button_rect.width - text.get_width()) // 2,
                                  button_rect.y + (button_rect.height - text.get_height()) // 2))
        else:
            # Draw rigid body mode UI
            font = pygame.font.Font(None, 24)
            
            # Draw mode indicator
            mode_text = font.render("RIGID BODY MODE", True, (255, 0, 0))
            screen.blit(mode_text, (10, self.height - self.gui_height + 5))
            
            # Draw current selections
            shape_text = font.render(f"Shape: {self.selected_shape.upper()} (1)", True, (0, 0, 0))
            screen.blit(shape_text, (200, self.height - self.gui_height + 5))
            
            material_text = font.render(f"Material: {self.selected_material.upper()} (2)", True, (0, 0, 0))
            screen.blit(material_text, (400, self.height - self.gui_height + 5))
            
            # Draw controls help
            help_text = font.render("G:gravity TAB:mode ←→:rotate DEL:delete", True, (0, 0, 0))
            screen.blit(help_text, (10, self.height - self.gui_height//2 + 5))