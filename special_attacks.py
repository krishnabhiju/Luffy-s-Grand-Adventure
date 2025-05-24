import pygame
import math
import random

# Special attack classes
class SpecialAttack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.damage = 1
    
    def update(self):
        pass
    
    def draw(self, surface):
        pass
    
    def check_collision(self, pirate):
        return False

class SwordSlash(SpecialAttack):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.life = 30
        self.width = 5
        self.color = (200, 200, 200)  # Silver color
        self.damage = 2
        
        # Calculate direction
        dx = end_x - start_x
        dy = end_y - start_y
        self.length = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction
        if self.length > 0:
            self.dx = dx / self.length
            self.dy = dy / self.length
        else:
            self.dx = 0
            self.dy = 0
        
        # Animation variables
        self.current_length = 0
        self.max_length = self.length
        self.extending = True
        self.extension_speed = 40
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.active = False
            return
        
        if self.extending:
            self.current_length = min(self.current_length + self.extension_speed, self.max_length)
            if self.current_length >= self.max_length:
                self.extending = False
        else:
            self.current_length = max(self.current_length - self.extension_speed, 0)
            if self.current_length <= 0:
                self.active = False
    
    def draw(self, surface):
        end_x = self.start_x + self.dx * self.current_length
        end_y = self.start_y + self.dy * self.current_length
        
        # Draw slash line
        pygame.draw.line(surface, self.color, (self.start_x, self.start_y), 
                         (end_x, end_y), self.width)
        
        # Draw slash effect
        for _ in range(5):
            offset = random.randint(5, 15)
            offset_x = random.uniform(-offset, offset)
            offset_y = random.uniform(-offset, offset)
            pygame.draw.line(surface, (255, 255, 255), 
                            (self.start_x + offset_x, self.start_y + offset_y), 
                            (end_x + offset_x, end_y + offset_y), 2)
    
    def check_collision(self, pirate):
        # Vector from start to end of slash
        slash_dx = self.dx * self.current_length
        slash_dy = self.dy * self.current_length
        
        # Vector from start of slash to pirate
        pirate_dx = pirate.x - self.start_x
        pirate_dy = pirate.y - self.start_y
        
        # Calculate dot product
        dot_product = pirate_dx * slash_dx + pirate_dy * slash_dy
        
        # If dot product is negative, pirate is behind the start point
        if dot_product < 0:
            distance = math.sqrt(pirate_dx**2 + pirate_dy**2)
            return distance < pirate.size
        
        # If dot product is greater than the squared length of the slash,
        # pirate is beyond the end point
        slash_length_squared = slash_dx**2 + slash_dy**2
        if dot_product > slash_length_squared:
            end_x = self.start_x + slash_dx
            end_y = self.start_y + slash_dy
            distance = math.sqrt((pirate.x - end_x)**2 + (pirate.y - end_y)**2)
            return distance < pirate.size
        
        # Calculate the projection of pirate position onto the slash line
        projection = dot_product / max(0.001, slash_length_squared)
        
        # Calculate the closest point on the slash line to the pirate
        closest_x = self.start_x + projection * slash_dx
        closest_y = self.start_y + projection * slash_dy
        
        # Calculate distance from pirate to the closest point
        distance = math.sqrt((pirate.x - closest_x)**2 + (pirate.y - closest_y)**2)
        
        return distance < pirate.size + self.width

class ThunderAttack(SpecialAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.life = 30
        self.radius = 30
        self.damage = 3
        self.segments = []
        
        # Create lightning segments
        prev_x, prev_y = x, 0  # Start from top of screen
        while prev_y < y:
            next_y = prev_y + random.randint(10, 30)
            next_x = prev_x + random.randint(-15, 15)
            self.segments.append((prev_x, prev_y, next_x, next_y))
            prev_x, prev_y = next_x, next_y
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.active = False
    
    def draw(self, surface):
        # Draw lightning bolt
        for i, (x1, y1, x2, y2) in enumerate(self.segments):
            color = (255, 255, 100) if i % 2 == 0 else (200, 200, 255)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
        
        # Draw impact circle
        if self.life > 20:
            radius = (30 - self.life) * 2
            pygame.draw.circle(surface, (255, 255, 200, 100), (self.x, self.y), radius)
    
    def check_collision(self, pirate):
        distance = math.sqrt((pirate.x - self.x)**2 + (pirate.y - self.y)**2)
        return distance < pirate.size + self.radius

class FireStar(SpecialAttack):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.speed = 10
        self.radius = 8
        self.damage = 1
        self.particles = []
        
        # Calculate direction
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction
        if length > 0:
            self.dx = dx / length * self.speed
            self.dy = dy / length * self.speed
        else:
            self.dx = 0
            self.dy = 0
    
    def update(self):
        # Move projectile
        self.current_x += self.dx
        self.current_y += self.dy
        
        # Add fire particles
        self.particles.append({
            'x': self.current_x,
            'y': self.current_y,
            'size': random.randint(3, 6),
            'life': random.randint(5, 15)
        })
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Check if out of bounds
        if (self.current_x < 0 or self.current_x > 800 or 
            self.current_y < 0 or self.current_y > 600):
            self.active = False
    
    def draw(self, surface):
        # Draw fire particles
        for particle in self.particles:
            size = particle['size']
            alpha = min(255, particle['life'] * 20)
            color = (255, min(255, 100 + particle['life'] * 10), 0, alpha)
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            surface.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Draw main projectile
        pygame.draw.circle(surface, (255, 200, 0), (int(self.current_x), int(self.current_y)), self.radius)
    
    def check_collision(self, pirate):
        distance = math.sqrt((pirate.x - self.current_x)**2 + (pirate.y - self.current_y)**2)
        if distance < pirate.size + self.radius:
            self.active = False
            return True
        return False

class DiableJambe(SpecialAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 0
        self.max_radius = 150
        self.expansion_speed = 10
        self.damage = 2
        self.color = (255, 100, 0, 150)
    
    def update(self):
        self.radius += self.expansion_speed
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, surface):
        # Create a surface with alpha for transparency
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))
        
        # Draw fire effects
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.7, 1.0) * self.radius
            size = random.randint(5, 15)
            
            flame_x = self.x + math.cos(angle) * distance
            flame_y = self.y + math.sin(angle) * distance
            
            pygame.draw.circle(surface, (255, 200, 0), (int(flame_x), int(flame_y)), size)
    
    def check_collision(self, pirate):
        distance = math.sqrt((pirate.x - self.x)**2 + (pirate.y - self.y)**2)
        return distance < pirate.size + self.radius

class RadicalBeam(SpecialAttack):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.width = 0
        self.max_width = 30
        self.life = 45
        self.damage = 4
        
        # Calculate direction
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction and extend to edge of screen
        if length > 0:
            self.dx = dx / length * 1000  # Very long beam
            self.dy = dy / length * 1000
        else:
            self.dx = 0
            self.dy = 1000  # Default to downward if no direction
        
        self.beam_end_x = start_x + self.dx
        self.beam_end_y = start_y + self.dy
    
    def update(self):
        self.life -= 1
        
        # Beam grows then shrinks
        if self.life > 30:
            self.width = min(self.max_width, self.width + 3)
        else:
            self.width = max(0, self.width - 1)
        
        if self.life <= 0:
            self.active = False
    
    def draw(self, surface):
        # Draw beam
        pygame.draw.line(surface, (0, 200, 255), 
                        (self.start_x, self.start_y), 
                        (self.beam_end_x, self.beam_end_y), 
                        self.width)
        
        # Draw core of beam
        pygame.draw.line(surface, (255, 255, 255), 
                        (self.start_x, self.start_y), 
                        (self.beam_end_x, self.beam_end_y), 
                        self.width // 3)
        
        # Draw impact point
        pygame.draw.circle(surface, (0, 200, 255), 
                          (self.start_x, self.start_y), 
                          self.width // 2)
    
    def check_collision(self, pirate):
        # Vector from start to end of beam
        beam_dx = self.dx
        beam_dy = self.dy
        
        # Vector from start of beam to pirate
        pirate_dx = pirate.x - self.start_x
        pirate_dy = pirate.y - self.start_y
        
        # Calculate dot product
        dot_product = pirate_dx * beam_dx + pirate_dy * beam_dy
        
        # If dot product is negative, pirate is behind the start point
        if dot_product < 0:
            return False
        
        # Calculate the projection of pirate position onto the beam line
        beam_length_squared = beam_dx**2 + beam_dy**2
        projection = dot_product / max(0.001, beam_length_squared)
        
        # Calculate the closest point on the beam line to the pirate
        closest_x = self.start_x + projection * beam_dx
        closest_y = self.start_y + projection * beam_dy
        
        # Calculate distance from pirate to the closest point
        distance = math.sqrt((pirate.x - closest_x)**2 + (pirate.y - closest_y)**2)
        
        return distance < pirate.size + self.width/2

class WaterWave(SpecialAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 0
        self.max_radius = 200
        self.expansion_speed = 8
        self.damage = 1
        self.push_strength = 10
    
    def update(self):
        self.radius += self.expansion_speed
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, surface):
        # Draw wave circles
        for r in range(int(self.radius), 0, -20):
            alpha = max(0, 150 - r * 150 // self.max_radius)
            color = (0, 100, 255, alpha)
            
            # Create a surface with alpha for transparency
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (r, r), r, 10)
            surface.blit(s, (self.x - r, self.y - r))
    
    def check_collision(self, pirate):
        distance = math.sqrt((pirate.x - self.x)**2 + (pirate.y - self.y)**2)
        
        # If pirate is within the wave radius
        if self.radius - 20 < distance < self.radius:
            # Calculate push direction (away from center)
            if distance > 0:
                push_dx = (pirate.x - self.x) / distance * self.push_strength
                push_dy = (pirate.y - self.y) / distance * self.push_strength
                
                # Apply push effect
                pirate.x += push_dx
                pirate.y += push_dy
            
            return True
        return False
