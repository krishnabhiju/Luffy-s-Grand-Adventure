import pygame
import random
import math

# Power-up classes
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.collected = False
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.bob_direction = 1
        self.lifetime = 600  # 10 seconds at 60 FPS
    
    def update(self):
        # Bob up and down
        self.bob_offset += self.bob_speed * self.bob_direction
        if abs(self.bob_offset) > 5:
            self.bob_direction *= -1
        
        # Decrease lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.collected = True
    
    def draw(self, surface):
        pass
    
    def apply_effect(self, game_state_data):
        pass
    
    def check_collision(self, luffy):
        distance = math.sqrt((self.x - luffy.x)**2 + (self.y - luffy.y)**2)
        return distance < self.radius + luffy.radius

class MeatPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (200, 100, 100)  # Meat color
    
    def draw(self, surface):
        # Draw meat
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y + self.bob_offset)), 
                          self.radius)
        pygame.draw.circle(surface, (255, 200, 200), 
                          (int(self.x - self.radius/3), int(self.y + self.bob_offset - self.radius/3)), 
                          self.radius/4)
        
        # Draw bone
        pygame.draw.rect(surface, (255, 255, 255), 
                        (self.x - self.radius/2, self.y + self.bob_offset - self.radius, 
                         self.radius/4, self.radius*1.5))
    
    def apply_effect(self, game_state_data):
        # Clear all pirates (like a screen clear)
        for pirate in game_state_data['pirates'][:]:
            game_state_data['pirates'].remove(pirate)
            game_state_data['score'] += 1
        return "Meat Power-Up: All pirates defeated!"

class DevilFruitPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.pattern = []
        
        # Create swirl pattern
        for i in range(10):
            self.pattern.append({
                'angle': random.uniform(0, 2*math.pi),
                'distance': random.uniform(0, self.radius*0.8),
                'size': random.randint(3, 6)
            })
    
    def draw(self, surface):
        # Draw devil fruit
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y + self.bob_offset)), 
                          self.radius)
        
        # Draw swirl pattern
        for p in self.pattern:
            px = self.x + math.cos(p['angle']) * p['distance']
            py = self.y + self.bob_offset + math.sin(p['angle']) * p['distance']
            pygame.draw.circle(surface, (50, 50, 50), 
                              (int(px), int(py)), 
                              p['size'])
    
    def apply_effect(self, game_state_data):
        # Activate Gear Fourth for Luffy (temporary power boost)
        game_state_data['gear_fourth_active'] = True
        game_state_data['gear_fourth_time'] = 600  # 10 seconds
        return "Devil Fruit Power-Up: Gear Fourth activated!"

class LogPosePowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, surface):
        # Draw log pose (compass)
        pygame.draw.circle(surface, (200, 200, 200), 
                          (int(self.x), int(self.y + self.bob_offset)), 
                          self.radius)
        pygame.draw.circle(surface, (255, 255, 255), 
                          (int(self.x), int(self.y + self.bob_offset)), 
                          self.radius - 3)
        
        # Draw needle
        angle = pygame.time.get_ticks() / 1000
        end_x = self.x + math.cos(angle) * (self.radius - 5)
        end_y = self.y + self.bob_offset + math.sin(angle) * (self.radius - 5)
        pygame.draw.line(surface, (255, 0, 0), 
                        (self.x, self.y + self.bob_offset), 
                        (end_x, end_y), 2)
    
    def apply_effect(self, game_state_data):
        # Advance to next island
        game_state_data['current_island'] += 1
        if game_state_data['current_island'] >= len(game_state_data['islands']):
            game_state_data['current_island'] = 0
        
        # Trigger boss battle
        game_state_data['boss_battle'] = True
        return f"Log Pose Power-Up: Navigating to {game_state_data['islands'][game_state_data['current_island']]}!"

class TreasurePowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, surface):
        # Draw treasure chest
        pygame.draw.rect(surface, (139, 69, 19), 
                        (self.x - self.radius, self.y + self.bob_offset - self.radius/2, 
                         self.radius*2, self.radius), 0)
        pygame.draw.rect(surface, (255, 215, 0), 
                        (self.x - self.radius + 2, self.y + self.bob_offset - self.radius/2 + 2, 
                         self.radius*2 - 4, self.radius - 4), 0)
        
        # Draw lock
        pygame.draw.rect(surface, (100, 100, 100), 
                        (self.x - self.radius/4, self.y + self.bob_offset - self.radius/2 - self.radius/4, 
                         self.radius/2, self.radius/2), 0)
    
    def apply_effect(self, game_state_data):
        # Add bonus points
        bonus = random.randint(5, 15)
        game_state_data['score'] += bonus
        return f"Treasure Power-Up: Found {bonus} bonus points!"

class RumbleBallPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, surface):
        # Draw rumble ball (yellow pill)
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(self.x), int(self.y + self.bob_offset)), 
                          self.radius)
        pygame.draw.line(surface, (200, 200, 0), 
                        (self.x - self.radius, self.y + self.bob_offset), 
                        (self.x + self.radius, self.y + self.bob_offset), 2)
    
    def apply_effect(self, game_state_data):
        # Unlock a random crew member if not already unlocked
        unlockable_crew = [cm for cm in game_state_data['crew_members'] if not cm.unlocked]
        if unlockable_crew:
            crew_member = random.choice(unlockable_crew)
            crew_member.unlocked = True
            return f"Rumble Ball Power-Up: {crew_member.name} joined your crew!"
        else:
            # If all crew members are unlocked, give bonus points
            game_state_data['score'] += 10
            return "Rumble Ball Power-Up: +10 bonus points!"
