import pygame
import random
import math

# Boss classes
class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50
        self.health = 20
        self.max_health = 20
        self.speed = 1.0
        self.dx = 0
        self.dy = 0
        self.attack_cooldown = 0
        self.attack_pattern = 0
        self.defeated = False
        self.name = "Boss"
        
        # Animation variables
        self.frame = 0
        self.animation_speed = 0.1
    
    def update(self, luffy_x, luffy_y):
        # Basic movement toward Luffy
        dx = luffy_x - self.x
        dy = luffy_y - self.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        
        self.dx = dx / distance * self.speed
        self.dy = dy / distance * self.speed
        
        self.x += self.dx
        self.y += self.dy
        
        # Update animation
        self.frame += self.animation_speed
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def draw(self, surface):
        # Draw boss body
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), self.size)
        
        # Draw health bar
        health_width = self.size * 2
        health_height = 10
        health_x = self.x - health_width/2
        health_y = self.y - self.size - 20
        
        # Background
        pygame.draw.rect(surface, (100, 100, 100), 
                        (health_x, health_y, health_width, health_height))
        
        # Health
        health_percent = self.health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), 
                        (health_x, health_y, health_width * health_percent, health_height))
        
        # Draw name
        font = pygame.font.Font(None, 24)
        name_text = font.render(self.name, True, (255, 255, 255))
        surface.blit(name_text, (self.x - name_text.get_width()/2, health_y - 20))
    
    def attack(self, game_state_data):
        # Override in subclasses
        pass
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.defeated = True
        return self.defeated
    
    def collides_with_luffy(self, luffy):
        distance = math.sqrt((self.x - luffy.x) ** 2 + (self.y - luffy.y) ** 2)
        return distance < (self.size + luffy.radius)

class Arlong(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Arlong"
        self.health = 15
        self.max_health = 15
        self.size = 40
        self.color = (0, 100, 200)  # Blue-ish
        self.attack_cooldown_max = 120
    
    def draw(self, surface):
        # Draw Arlong body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        # Draw shark features
        # Nose
        pygame.draw.polygon(surface, (0, 50, 150), [
            (self.x, self.y - self.size/2),
            (self.x - self.size/3, self.y - self.size),
            (self.x + self.size/3, self.y - self.size)
        ])
        
        # Teeth
        teeth_width = self.size * 0.8
        teeth_height = self.size * 0.3
        pygame.draw.rect(surface, (255, 255, 255), 
                       (self.x - teeth_width/2, self.y, 
                        teeth_width, teeth_height))
        
        # Draw health bar and name
        super().draw(surface)
    
    def attack(self, game_state_data):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
            if self.attack_pattern == 0:
                # Water shot attack
                for i in range(3):
                    angle = math.pi/4 * (i - 1)
                    dx = math.cos(angle) * 400
                    dy = math.sin(angle) * 400
                    game_state_data['boss_attacks'].append(
                        WaterShot(self.x, self.y, self.x + dx, self.y + dy)
                    )
            elif self.attack_pattern == 1:
                # Summon fish-men
                for _ in range(2):
                    pirate = game_state_data['Pirate']()  # Create pirate with default constructor
                    # Override pirate properties
                    pirate.x = self.x
                    pirate.y = self.y
                    pirate.type = "fishman"
                    pirate.color = (0, 100, 150)
                    pirate.health = 2
                    game_state_data['pirates'].append(pirate)
            else:
                # Shark tooth projectile
                game_state_data['boss_attacks'].append(
                    SharkToothAttack(self.x, self.y, game_state_data['luffy'].x, game_state_data['luffy'].y)
                )

class Crocodile(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Crocodile"
        self.health = 25
        self.max_health = 25
        self.size = 45
        self.color = (200, 180, 140)  # Sand color
        self.attack_cooldown_max = 150
        self.sand_form = False
        self.sand_timer = 0
    
    def update(self, luffy_x, luffy_y):
        if self.sand_form:
            # Move faster in sand form
            self.sand_timer -= 1
            if self.sand_timer <= 0:
                self.sand_form = False
            
            # Random movement in sand form
            self.x += random.uniform(-3, 3)
            self.y += random.uniform(-3, 3)
        else:
            # Normal movement
            super().update(luffy_x, luffy_y)
    
    def draw(self, surface):
        if self.sand_form:
            # Draw sand cloud
            for _ in range(20):
                offset_x = random.randint(-self.size, self.size)
                offset_y = random.randint(-self.size, self.size)
                if offset_x**2 + offset_y**2 <= self.size**2:
                    sand_size = random.randint(5, 15)
                    pygame.draw.circle(surface, self.color, 
                                      (int(self.x + offset_x), int(self.y + offset_y)), 
                                      sand_size)
        else:
            # Draw Crocodile body
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
            
            # Draw hook hand
            hook_x = self.x + self.size * 0.8
            hook_y = self.y
            pygame.draw.line(surface, (200, 200, 200), 
                            (self.x + self.size/2, self.y), 
                            (hook_x, hook_y), 5)
            pygame.draw.arc(surface, (200, 200, 200), 
                           (hook_x - 10, hook_y - 10, 20, 20), 
                           math.pi/2, math.pi*3/2, 5)
        
        # Draw health bar and name
        super().draw(surface)
    
    def attack(self, game_state_data):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
            if self.attack_pattern == 0:
                # Sand tornado
                game_state_data['boss_attacks'].append(
                    SandTornado(self.x, self.y)
                )
            elif self.attack_pattern == 1:
                # Transform to sand
                self.sand_form = True
                self.sand_timer = 180  # 3 seconds
            else:
                # Ground desiccation
                game_state_data['boss_attacks'].append(
                    GroundDesiccation(self.x, self.y)
                )

class Enel(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Enel"
        self.health = 30
        self.max_health = 30
        self.size = 40
        self.color = (255, 255, 100)  # Yellow/lightning color
        self.attack_cooldown_max = 90
        self.teleport_cooldown = 0
    
    def update(self, luffy_x, luffy_y):
        # Occasionally teleport
        self.teleport_cooldown -= 1
        if self.teleport_cooldown <= 0:
            self.teleport_cooldown = 180  # 3 seconds
            # Teleport to a random position
            self.x = random.randint(100, 700)
            self.y = random.randint(100, 500)
        else:
            # Normal movement
            super().update(luffy_x, luffy_y)
    
    def draw(self, surface):
        # Draw Enel body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        # Draw lightning effects
        for _ in range(5):
            start_x = self.x + random.uniform(-self.size, self.size)
            start_y = self.y + random.uniform(-self.size, self.size)
            end_x = start_x + random.uniform(-20, 20)
            end_y = start_y + random.uniform(-20, 20)
            pygame.draw.line(surface, (255, 255, 255), 
                            (start_x, start_y), 
                            (end_x, end_y), 2)
        
        # Draw health bar and name
        super().draw(surface)
    
    def attack(self, game_state_data):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_cooldown_max
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
            if self.attack_pattern == 0:
                # El Thor (lightning strike)
                game_state_data['boss_attacks'].append(
                    ElThor(game_state_data['luffy'].x, game_state_data['luffy'].y)
                )
            elif self.attack_pattern == 1:
                # Raigo (thunder cloud)
                game_state_data['boss_attacks'].append(
                    Raigo(self.x, self.y)
                )
            else:
                # Multiple lightning bolts
                for _ in range(5):
                    x = random.randint(100, 700)
                    y = random.randint(100, 500)
                    game_state_data['boss_attacks'].append(
                        LightningBolt(x, y)
                    )

# Boss attack classes
class BossAttack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.damage = 1
    
    def update(self):
        pass
    
    def draw(self, surface):
        pass
    
    def check_collision(self, luffy):
        return False

class WaterShot(BossAttack):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.speed = 8
        self.radius = 10
        self.damage = 1
        
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
        
        # Check if out of bounds
        if (self.current_x < 0 or self.current_x > 800 or 
            self.current_y < 0 or self.current_y > 600):
            self.active = False
    
    def draw(self, surface):
        # Draw water projectile
        pygame.draw.circle(surface, (0, 100, 255), 
                          (int(self.current_x), int(self.current_y)), 
                          self.radius)
        
        # Draw water trail
        for i in range(5):
            trail_x = self.current_x - self.dx * i * 2
            trail_y = self.current_y - self.dy * i * 2
            pygame.draw.circle(surface, (100, 200, 255), 
                              (int(trail_x), int(trail_y)), 
                              self.radius - i * 1.5)
    
    def check_collision(self, luffy):
        distance = math.sqrt((luffy.x - self.current_x)**2 + (luffy.y - self.current_y)**2)
        if distance < luffy.radius + self.radius:
            self.active = False
            return True
        return False

class SharkToothAttack(BossAttack):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__(start_x, start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.speed = 10
        self.size = 15
        self.damage = 2
        self.rotation = 0
        self.rotation_speed = 0.2
        
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
        
        # Rotate
        self.rotation += self.rotation_speed
        
        # Check if out of bounds
        if (self.current_x < 0 or self.current_x > 800 or 
            self.current_y < 0 or self.current_y > 600):
            self.active = False
    
    def draw(self, surface):
        # Draw shark tooth
        points = []
        for i in range(3):
            angle = self.rotation + i * (2*math.pi/3)
            x = self.current_x + math.cos(angle) * self.size
            y = self.current_y + math.sin(angle) * self.size
            points.append((x, y))
        
        pygame.draw.polygon(surface, (255, 255, 255), points)
    
    def check_collision(self, luffy):
        distance = math.sqrt((luffy.x - self.current_x)**2 + (luffy.y - self.current_y)**2)
        if distance < luffy.radius + self.size:
            self.active = False
            return True
        return False

class SandTornado(BossAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 0
        self.max_radius = 100
        self.expansion_speed = 2
        self.damage = 1
        self.lifetime = 180  # 3 seconds
        self.particles = []
        
        # Create initial particles
        for _ in range(50):
            self.add_particle()
    
    def add_particle(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, self.radius)
        speed = random.uniform(1, 3)
        size = random.uniform(3, 8)
        
        self.particles.append({
            'x': self.x + math.cos(angle) * distance,
            'y': self.y + math.sin(angle) * distance,
            'angle': angle,
            'distance': distance,
            'speed': speed,
            'size': size,
            'rotation': random.uniform(0, 0.2)
        })
    
    def update(self):
        # Expand tornado
        if self.radius < self.max_radius:
            self.radius += self.expansion_speed
        
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
        
        # Add new particles
        if random.random() < 0.3:
            self.add_particle()
        
        # Update particles
        for particle in self.particles[:]:
            # Rotate particle around center
            particle['angle'] += particle['rotation']
            particle['distance'] = min(particle['distance'] + particle['speed'] * 0.1, self.radius)
            
            # Update position
            particle['x'] = self.x + math.cos(particle['angle']) * particle['distance']
            particle['y'] = self.y + math.sin(particle['angle']) * particle['distance']
            
            # Remove particles that go beyond the tornado
            if particle['distance'] >= self.radius:
                self.particles.remove(particle)
    
    def draw(self, surface):
        # Draw tornado particles
        for particle in self.particles:
            pygame.draw.circle(surface, (200, 180, 140), 
                              (int(particle['x']), int(particle['y'])), 
                              int(particle['size']))
    
    def check_collision(self, luffy):
        distance = math.sqrt((luffy.x - self.x)**2 + (luffy.y - self.y)**2)
        return distance < luffy.radius + self.radius

class GroundDesiccation(BossAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 0
        self.max_radius = 150
        self.expansion_speed = 5
        self.damage = 1
        self.cracks = []
        
        # Create cracks
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            self.cracks.append({
                'angle': angle,
                'length': 0,
                'width': random.uniform(2, 5),
                'segments': []
            })
    
    def update(self):
        # Expand effect
        self.radius += self.expansion_speed
        if self.radius >= self.max_radius:
            self.active = False
        
        # Update cracks
        for crack in self.cracks:
            crack['length'] = self.radius
            
            # Create crack segments
            if not crack['segments'] or crack['segments'][-1]['length'] < crack['length']:
                prev_segment = crack['segments'][-1] if crack['segments'] else {
                    'x': self.x,
                    'y': self.y,
                    'angle': crack['angle'],
                    'length': 0
                }
                
                new_length = prev_segment['length'] + random.uniform(10, 30)
                new_length = min(new_length, crack['length'])
                
                new_angle = prev_segment['angle'] + random.uniform(-0.3, 0.3)
                
                end_x = self.x + math.cos(new_angle) * new_length
                end_y = self.y + math.sin(new_angle) * new_length
                
                crack['segments'].append({
                    'x': end_x,
                    'y': end_y,
                    'angle': new_angle,
                    'length': new_length
                })
    
    def draw(self, surface):
        # Draw dried ground
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 180, 140, 100), (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))
        
        # Draw cracks
        for crack in self.cracks:
            prev_x, prev_y = self.x, self.y
            
            for segment in crack['segments']:
                pygame.draw.line(surface, (100, 80, 60), 
                                (prev_x, prev_y), 
                                (segment['x'], segment['y']), 
                                int(crack['width']))
                prev_x, prev_y = segment['x'], segment['y']
    
    def check_collision(self, luffy):
        distance = math.sqrt((luffy.x - self.x)**2 + (luffy.y - self.y)**2)
        return distance < luffy.radius + self.radius

class ElThor(BossAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.life = 60  # 1 second
        self.radius = 50
        self.damage = 3
        self.warning_time = 30
        self.segments = []
        
        # Create lightning segments
        if self.warning_time <= 0:
            self.create_lightning()
    
    def create_lightning(self):
        prev_x, prev_y = self.x, 0  # Start from top of screen
        while prev_y < self.y:
            next_y = prev_y + random.randint(10, 30)
            next_x = prev_x + random.randint(-15, 15)
            self.segments.append((prev_x, prev_y, next_x, next_y))
            prev_x, prev_y = next_x, next_y
    
    def update(self):
        if self.warning_time > 0:
            self.warning_time -= 1
            if self.warning_time <= 0:
                self.create_lightning()
        else:
            self.life -= 1
            if self.life <= 0:
                self.active = False
    
    def draw(self, surface):
        if self.warning_time > 0:
            # Draw warning circle
            pygame.draw.circle(surface, (255, 0, 0, 100), 
                              (int(self.x), int(self.y)), 
                              self.radius, 2)
        else:
            # Draw lightning bolt
            for i, (x1, y1, x2, y2) in enumerate(self.segments):
                color = (255, 255, 100) if i % 2 == 0 else (200, 200, 255)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
            
            # Draw impact circle
            pygame.draw.circle(surface, (255, 255, 200, 100), 
                              (int(self.x), int(self.y)), 
                              self.radius)
    
    def check_collision(self, luffy):
        if self.warning_time <= 0:
            distance = math.sqrt((luffy.x - self.x)**2 + (luffy.y - self.y)**2)
            return distance < luffy.radius + self.radius
        return False

class Raigo(BossAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 40
        self.max_radius = 80
        self.expansion_rate = 0.5
        self.damage = 2
        self.life = 180  # 3 seconds
        self.lightning_timer = 0
    
    def update(self):
        # Expand cloud
        if self.radius < self.max_radius:
            self.radius += self.expansion_rate
        
        # Move cloud slightly
        self.x += random.uniform(-1, 1)
        self.y += random.uniform(-1, 1)
        
        # Generate lightning occasionally
        self.lightning_timer -= 1
        if self.lightning_timer <= 0:
            self.lightning_timer = random.randint(10, 30)
            # Lightning would be added to game_state_data['boss_attacks'] in the main game loop
        
        # Update lifetime
        self.life -= 1
        if self.life <= 0:
            self.active = False
    
    def draw(self, surface):
        # Draw thunder cloud
        for _ in range(10):
            offset_x = random.randint(-int(self.radius), int(self.radius))
            offset_y = random.randint(-int(self.radius/2), int(self.radius/2))
            if offset_x**2 + offset_y**2 <= self.radius**2:
                cloud_size = random.randint(int(self.radius/3), int(self.radius/2))
                pygame.draw.circle(surface, (100, 100, 100), 
                                  (int(self.x + offset_x), int(self.y + offset_y)), 
                                  cloud_size)
        
        # Draw lightning inside cloud
        if random.random() < 0.3:
            for _ in range(3):
                start_x = self.x + random.uniform(-self.radius/2, self.radius/2)
                start_y = self.y + random.uniform(-self.radius/2, self.radius/2)
                end_x = start_x + random.uniform(-10, 10)
                end_y = start_y + random.uniform(-10, 10)
                pygame.draw.line(surface, (255, 255, 100), 
                                (start_x, start_y), 
                                (end_x, end_y), 2)
    
    def check_collision(self, luffy):
        distance = math.sqrt((luffy.x - self.x)**2 + (luffy.y - self.y)**2)
        return distance < luffy.radius + self.radius

class LightningBolt(BossAttack):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.life = 20
        self.damage = 1
        self.warning_time = 15
        self.segments = []
    
    def update(self):
        if self.warning_time > 0:
            self.warning_time -= 1
        else:
            self.life -= 1
            if self.life <= 0:
                self.active = False
            
            # Create lightning segments if not already created
            if not self.segments:
                prev_x, prev_y = self.x, 0  # Start from top of screen
                while prev_y < self.y:
                    next_y = prev_y + random.randint(10, 30)
                    next_x = prev_x + random.randint(-10, 10)
                    self.segments.append((prev_x, prev_y, next_x, next_y))
                    prev_x, prev_y = next_x, next_y
    
    def draw(self, surface):
        if self.warning_time > 0:
            # Draw warning indicator
            pygame.draw.circle(surface, (255, 255, 0), 
                              (int(self.x), int(self.y)), 
                              10, 2)
        else:
            # Draw lightning bolt
            for i, (x1, y1, x2, y2) in enumerate(self.segments):
                color = (255, 255, 100) if i % 2 == 0 else (200, 200, 255)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)
    
    def check_collision(self, luffy):
        if self.warning_time <= 0:
            distance = math.sqrt((luffy.x - self.x)**2 + (luffy.y - self.y)**2)
            return distance < luffy.radius + 20
        return False
