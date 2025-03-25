import math
import pygame

# Shape definitions
SHAPES = {
    "box": {
        "cells": [(x, y) for x in range(-1, 2) for y in range(-1, 2)],
        "label": "BOX",
        "description": "3x3 solid box"
    },
    "ball": {
        "cells": [(0,0), (0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)],
        "label": "BALL",
        "description": "Circular shape"
    },
    "beam": {
        "cells": [(x, 0) for x in range(-2, 3)] + [(x, 1) for x in range(-2, 3)],
        "label": "BEAM",
        "description": "5x2 horizontal beam"
    },
    "triangle": {
        "cells": [(0,0), (-1,1), (0,1), (1,1), (-2,2), (-1,2), (0,2), (1,2), (2,2)],
        "label": "TRI",
        "description": "Triangle shape"
    }
}

# Material definitions
RIGID_MATERIALS = {
    "wood_block": {
        "name": "Wooden Block",
        "label": "WOOD",
        "density": 400,
        "friction": 0.5,
        "color": (139, 69, 19),
        "pushes_particles": True
    },
    "metal_block": {
        "name": "Metal Block",
        "label": "METL",
        "density": 1000,
        "friction": 0.2,
        "color": (192, 192, 192),
        "pushes_particles": True
    },
    "rubber": {
        "name": "Rubber",
        "label": "RUBR",
        "density": 200,
        "friction": 0.7,
        "color": (60, 60, 60),
        "pushes_particles": False
    },
    "crystal": {
        "name": "Crystal",
        "label": "CRYS",
        "density": 800,
        "friction": 0.1,
        "color": (200, 200, 255),
        "pushes_particles": True
    }
}

class RigidBody:
    def __init__(self, shape_type, material, x, y):
        """Initialize a rigid body with given shape and material"""
        if shape_type not in SHAPES:
            raise ValueError(f"Invalid shape type: {shape_type}")
        if material not in RIGID_MATERIALS:
            raise ValueError(f"Invalid material type: {material}")

        self.shape_type = shape_type
        self.material = RIGID_MATERIALS[material]
        self.x = x  # Center position
        self.y = y
        self.rotation = 0  # In degrees
        self.velocity = [0, 0]
        self.angular_velocity = 0
        self.gravity_enabled = False
        self.force = [0, 0]  # Current force being applied
        self.selected = False  # Track if this body is currently selected
        self.cells = self._generate_cells()
        self.mass = self._calculate_mass()

    def _generate_cells(self):
        """Generate the list of cells that make up this rigid body"""
        return SHAPES[self.shape_type]["cells"]

    def _calculate_mass(self):
        """Calculate mass based on shape size and material density"""
        return len(self.cells) * self.material["density"] / 100.0

    def get_world_cells(self):
        """Get cell positions in world coordinates, accounting for rotation"""
        world_cells = []
        for cell_x, cell_y in self.cells:
            if self.rotation == 0:
                # Fast path for no rotation
                world_x = int(self.x + cell_x)
                world_y = int(self.y + cell_y)
            else:
                # Apply rotation around center point
                angle_rad = math.radians(self.rotation)
                cos_angle = math.cos(angle_rad)
                sin_angle = math.sin(angle_rad)
                
                rotated_x = cell_x * cos_angle - cell_y * sin_angle
                rotated_y = cell_x * sin_angle + cell_y * cos_angle
                
                world_x = int(self.x + rotated_x)
                world_y = int(self.y + rotated_y)
            
            world_cells.append((world_x, world_y))
        return world_cells

    def apply_force(self, fx, fy):
        """Apply a force to the rigid body"""
        self.force[0] += fx
        self.force[1] += fy

    def update(self, dt):
        """Update physics for the rigid body"""
        # Apply accumulated forces
        ax = self.force[0] / self.mass
        ay = self.force[1] / self.mass
        
        # Update velocity
        self.velocity[0] += ax * dt
        self.velocity[1] += ay * dt
        
        # Apply gravity if enabled
        if self.gravity_enabled:
            self.velocity[1] += 9.81 * dt  # Standard gravity
        
        # Update position
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        
        # Apply damping
        self.velocity[0] *= 0.98  # Air resistance
        self.velocity[1] *= 0.98
        
        # Update rotation
        self.rotation += self.angular_velocity * dt
        self.angular_velocity *= 0.98  # Rotational damping
        
        # Reset forces
        self.force = [0, 0]

    def draw(self, screen, particle_size):
        """Draw the rigid body on the screen"""
        # Draw each cell of the rigid body
        for world_x, world_y in self.get_world_cells():
            screen_x = world_x * particle_size
            screen_y = world_y * particle_size
            
            # Create cell surface with alpha for selection highlight
            cell_surface = pygame.Surface((particle_size, particle_size))
            cell_surface.fill(self.material["color"])
            
            if self.selected:
                # Add selection highlight
                highlight = pygame.Surface((particle_size, particle_size))
                highlight.fill((255, 255, 255))
                highlight.set_alpha(64)
                cell_surface.blit(highlight, (0, 0))
            
            screen.blit(cell_surface, (screen_x, screen_y))

    def to_dict(self):
        """Serialize the rigid body for saving"""
        return {
            "shape_type": self.shape_type,
            "material": next(k for k, v in RIGID_MATERIALS.items() if v == self.material),
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "velocity": self.velocity,
            "angular_velocity": self.angular_velocity,
            "gravity_enabled": self.gravity_enabled
        }

    @classmethod
    def from_dict(cls, data):
        """Create a rigid body from serialized data"""
        body = cls(data["shape_type"], data["material"], data["x"], data["y"])
        body.rotation = data["rotation"]
        body.velocity = data["velocity"]
        body.angular_velocity = data.get("angular_velocity", 0)
        body.gravity_enabled = data.get("gravity_enabled", False)
        return body