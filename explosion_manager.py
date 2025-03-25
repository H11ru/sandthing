import math

class ExplosionManager:
    def __init__(self):
        self.explosion_force_factor = 0.3  # Reduced force for rigid bodies
        
    def apply_explosion_force(self, source_x, source_y, radius, rigid_body):
        """Apply explosion force to a rigid body based on distance from explosion"""
        # Calculate distance from explosion to rigid body center
        dx = rigid_body.x - source_x
        dy = rigid_body.y - source_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= radius:
            # Calculate force magnitude (decreases with distance)
            force_magnitude = (1 - distance/radius) * self.explosion_force_factor
            
            # Calculate force direction
            angle = math.atan2(dy, dx)
            force_x = math.cos(angle) * force_magnitude * 1000  # Scale force for game units
            force_y = math.sin(angle) * force_magnitude * 1000
            
            # Apply force to rigid body
            rigid_body.apply_force(force_x, force_y)
            
            # Add some rotation based on offset from center
            # This creates more realistic explosion effects
            perpendicular_distance = abs(dx * math.cos(angle + math.pi/2))
            rotation_force = perpendicular_distance * force_magnitude * 0.1
            rigid_body.angular_velocity += rotation_force if random.random() > 0.5 else -rotation_force

    def handle_explosion(self, x, y, radius, rigid_bodies):
        """Handle explosion effects on all rigid bodies in range"""
        for body in rigid_bodies:
            self.apply_explosion_force(x, y, radius, body)
            
    def create_particle_explosion(self, x, y, radius, grid, particle_handler):
        """Create particle explosion effects"""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:  # Circular explosion
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                        if random.random() < 0.1:  # 10% chance for fire particle
                            particle_handler.create_particle(nx, ny, "fire")