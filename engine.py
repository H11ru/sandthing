import pygame
from particle_system import ParticleSystem
from physics_engine import PhysicsEngine
from ui_manager import UIManager
from achievement_system import AchievementSystem

class GameEngine:
    def __init__(self):
        # Constants
        self.WIDTH = 800
        self.HEIGHT = 480
        self.PARTICLE_SIZE = 5
        self.GUI_HEIGHT = 40
        self.FPS = 60
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Initialize subsystems
        self.particle_system = ParticleSystem(self.WIDTH, self.HEIGHT, self.PARTICLE_SIZE, self.GUI_HEIGHT)
        self.physics_engine = PhysicsEngine(self.particle_system)
        self.ui_manager = UIManager(self.WIDTH, self.HEIGHT, self.GUI_HEIGHT, self.PARTICLE_SIZE)
        self.achievement_system = AchievementSystem()
        
        # Import rigid body
        from rigid_body import RigidBody
        
        # Game state
        self.simulation_running = False
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.simulation_running = not self.simulation_running
                elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.particle_system.clear_grid()
                    self.physics_engine.rigid_bodies.clear()  # Also clear rigid bodies
            
            # Let UI handle the event with physics engine access
            self.ui_manager.handle_event(event, self.particle_system, self.physics_engine)

    def update(self):
        if self.simulation_running:
            self.physics_engine.update()
        
        self.achievement_system.update(1/self.FPS)
        self.achievement_system.check_achievements(self.particle_system)

    def render(self):
        self.screen.fill((255, 255, 255))
        
        # Render particles and rigid bodies
        self.particle_system.draw(self.screen)
        self.physics_engine.draw(self.screen)
        
        # Render UI
        self.ui_manager.draw(self.screen)
        
        # Render achievements
        self.achievement_system.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.FPS)
        
        pygame.quit()

if __name__ == "__main__":
    engine = GameEngine()
    engine.run()