import pygame
from data import achievements

class AchievementSystem:
    def __init__(self):
        self.ACHIEVEMENT_DISPLAY_TIME = 3  # Seconds to display achievement notification
        self.active_achievements = []      # Currently displaying achievements
        self.achievement_counts = {}       # Track counts for achievement conditions
        self.achievement_font = None       # Font for achievement text
        
    def update(self, dt):
        """Update achievement display timers"""
        # Remove expired achievements
        new_achievements = []
        for ach in self.active_achievements:
            ach['time'] -= dt
            if ach['time'] > 0:
                new_achievements.append(ach)
        self.active_achievements = new_achievements

    def check_achievements(self, particle_system):
        """Check for newly completed achievements"""
        for achievement_id, achievement in achievements.items():
            if not achievement['achieved']:
                if achievement['type'] in ['Achievement', 'Challenge', 'SECRET']:
                    condition = achievement['condit'][0]
                    
                    if condition == 'liferanout':
                        particle_type = achievement['condit'][1]
                        required_amount = int(achievement['condit'][2])
                        
                        if particle_type not in self.achievement_counts:
                            self.achievement_counts[particle_type] = 0
                        
                        if self.achievement_counts[particle_type] >= required_amount:
                            self.unlock_achievement(achievement_id)
                    
                    elif condition == 'place':
                        particle_type = achievement['condit'][1]
                        if len(achievement['condit']) > 2:
                            required_amount = int(achievement['condit'][2])
                            if particle_type == '*':
                                # Any particle type counts
                                if sum(list(particle_system.placed.values())) >= required_amount:
                                    self.unlock_achievement(achievement_id)
                            else:
                                # Specific particle type
                                if particle_system.placed[particle_type] >= required_amount:
                                    self.unlock_achievement(achievement_id)
                        else:
                            # Check if any particle has been placed
                            if particle_system.placed[particle_type] > 0:
                                self.unlock_achievement(achievement_id)
                    
                    elif condition == 'place1ofall':
                        # Check if player has placed at least one of each particle type
                        if all(particle_system.placed[key] > 0 for key in particle_system.placed.keys()):
                            self.unlock_achievement(achievement_id)
                            
                    elif condition == 'exploded':
                        # Check if any/targeted particle has been exploded at correct count
                        if particle_system.exploded[particle_type] >= required_amount:
                            self.unlock_achievement(achievement_id)

    def unlock_achievement(self, achievement_id):
        """Unlock an achievement and show notification"""
        if not achievements[achievement_id]['achieved']:
            achievements[achievement_id]['achieved'] = True
            self.active_achievements.append({
                'name': achievements[achievement_id]['name'],
                'description': achievements[achievement_id]['description'],
                'time': self.ACHIEVEMENT_DISPLAY_TIME,
                'type': achievements[achievement_id]['type'],
            })

    def draw(self, screen):
        """Draw achievement notifications"""
        if not self.achievement_font:
            self.achievement_font = pygame.font.Font(None, 32)
        
        y_offset = 10
        for achievement in self.active_achievements:
            # Draw achievement notification
            text = f"{achievement['type']} Completed: {achievement['name']}"
            subtext = f"{achievement['description']}"
            text_surface = self.achievement_font.render(text, True, (255, 215, 0))
            subtext_surface = self.achievement_font.render(subtext, True, (255, 255, 255))
            
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