import pygame
import random
import math

# Island background classes
class Island:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.name = "Island"
        self.base_color = (0, 100, 200)  # Ocean blue
        self.elements = []
        self.create_elements()
    
    def create_elements(self):
        # Override in subclasses
        pass
    
    def draw(self, surface):
        # Draw base ocean
        surface.fill(self.base_color)
        
        # Draw elements
        for element in self.elements:
            element.draw(surface)
    
    def update(self):
        for element in self.elements:
            element.update()

class EastBlue(Island):
    def __init__(self, width, height):
        self.name = "East Blue"
        self.base_color = (0, 120, 200)  # Bright blue ocean
        super().__init__(width, height)
    
    def create_elements(self):
        # Create clouds
        for _ in range(10):
            self.elements.append(Cloud(
                random.randint(0, self.width),
                random.randint(20, self.height//3),
                random.randint(80, 200),
                random.randint(40, 80),
                random.uniform(0.2, 0.8)
            ))
        
        # Create small islands
        for _ in range(3):
            self.elements.append(SmallIsland(
                random.randint(100, self.width - 100),
                random.randint(100, self.height - 100),
                random.randint(50, 100)
            ))

class Alabasta(Island):
    def __init__(self, width, height):
        self.name = "Alabasta"
        self.base_color = (200, 180, 140)  # Desert sand color
        super().__init__(width, height)
    
    def create_elements(self):
        # Create sand dunes
        for _ in range(5):
            self.elements.append(SandDune(
                random.randint(0, self.width),
                random.randint(self.height//2, self.height),
                random.randint(100, 300),
                random.randint(50, 100)
            ))
        
        # Create palm trees
        for _ in range(8):
            self.elements.append(PalmTree(
                random.randint(50, self.width - 50),
                random.randint(self.height//2, self.height - 50),
                random.randint(30, 50)
            ))

class Skypiea(Island):
    def __init__(self, width, height):
        self.name = "Skypiea"
        self.base_color = (135, 206, 235)  # Sky blue
        super().__init__(width, height)
    
    def create_elements(self):
        # Create cloud islands
        for _ in range(4):
            self.elements.append(CloudIsland(
                random.randint(100, self.width - 100),
                random.randint(100, self.height - 100),
                random.randint(80, 150)
            ))
        
        # Create more clouds
        for _ in range(15):
            self.elements.append(Cloud(
                random.randint(0, self.width),
                random.randint(20, self.height - 100),
                random.randint(60, 150),
                random.randint(30, 60),
                random.uniform(0.1, 0.5)
            ))

class WaterSeven(Island):
    def __init__(self, width, height):
        self.name = "Water 7"
        self.base_color = (0, 80, 150)  # Deep blue water
        super().__init__(width, height)
    
    def create_elements(self):
        # Create buildings
        for _ in range(10):
            self.elements.append(Building(
                random.randint(50, self.width - 50),
                random.randint(self.height//2, self.height - 50),
                random.randint(30, 80),
                random.randint(80, 150)
            ))
        
        # Create water canals
        for _ in range(5):
            self.elements.append(Canal(
                random.randint(0, self.width),
                random.randint(self.height//2, self.height),
                random.randint(100, 300),
                random.randint(20, 40)
            ))

class ThrillerBark(Island):
    def __init__(self, width, height):
        self.name = "Thriller Bark"
        self.base_color = (50, 50, 70)  # Dark, spooky color
        super().__init__(width, height)
    
    def create_elements(self):
        # Create spooky trees
        for _ in range(15):
            self.elements.append(SpookyTree(
                random.randint(50, self.width - 50),
                random.randint(self.height//2, self.height - 50),
                random.randint(40, 80)
            ))
        
        # Create fog patches
        for _ in range(8):
            self.elements.append(FogPatch(
                random.randint(0, self.width),
                random.randint(0, self.height),
                random.randint(100, 200)
            ))

class Marineford(Island):
    def __init__(self, width, height):
        self.name = "Marineford"
        self.base_color = (0, 100, 180)  # Ocean blue
        super().__init__(width, height)
    
    def create_elements(self):
        # Create marine headquarters
        self.elements.append(MarineHQ(
            self.width // 2,
            self.height // 2,
            300,
            200
        ))
        
        # Create marine ships
        for _ in range(6):
            self.elements.append(Ship(
                random.randint(50, self.width - 50),
                random.randint(50, self.height - 50),
                random.randint(40, 80),
                (200, 200, 200)  # White for marine ships
            ))

# Background element classes
class BackgroundElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def update(self):
        pass
    
    def draw(self, surface):
        pass

class Cloud(BackgroundElement):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.speed = speed
    
    def update(self):
        self.x += self.speed
        if self.x > 800 + self.width:
            self.x = -self.width
    
    def draw(self, surface):
        pygame.draw.ellipse(surface, (230, 230, 230), 
                          (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(surface, (200, 200, 200), 
                          (self.x + self.width//4, self.y + self.height//4, 
                           self.width//2, self.height//2))

class SmallIsland(BackgroundElement):
    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.size = size
        self.color = (100, 200, 100)  # Green for grass
    
    def draw(self, surface):
        # Draw island
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        
        # Draw beach
        pygame.draw.circle(surface, (240, 220, 130), (self.x, self.y), self.size, 10)

class SandDune(BackgroundElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = (240, 220, 130)  # Sand color
    
    def draw(self, surface):
        # Draw sand dune as a semi-ellipse
        points = []
        for i in range(self.width):
            angle = math.pi * i / self.width
            x = self.x + i
            y = self.y - math.sin(angle) * self.height
            points.append((x, y))
        
        # Add bottom points to close the shape
        points.append((self.x + self.width, self.y))
        points.append((self.x, self.y))
        
        pygame.draw.polygon(surface, self.color, points)

class PalmTree(BackgroundElement):
    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.size = size
        self.trunk_color = (139, 69, 19)  # Brown
        self.leaf_color = (0, 150, 0)  # Green
    
    def draw(self, surface):
        # Draw trunk
        pygame.draw.rect(surface, self.trunk_color, 
                        (self.x - self.size//6, self.y - self.size, 
                         self.size//3, self.size))
        
        # Draw leaves
        for i in range(5):
            angle = math.pi/2 + i * math.pi/3
            length = self.size * 0.8
            end_x = self.x + math.cos(angle) * length
            end_y = self.y - self.size + math.sin(angle) * length
            
            # Draw leaf as a triangle
            pygame.draw.polygon(surface, self.leaf_color, [
                (self.x, self.y - self.size),
                (end_x - length/5, end_y - length/5),
                (end_x + length/5, end_y + length/5)
            ])

class CloudIsland(BackgroundElement):
    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.size = size
        self.cloud_color = (255, 255, 255)
        self.dirt_color = (150, 100, 50)
    
    def draw(self, surface):
        # Draw cloud base
        for i in range(5):
            offset_x = random.randint(-self.size//2, self.size//2)
            offset_y = random.randint(-self.size//4, self.size//4)
            pygame.draw.circle(surface, self.cloud_color, 
                              (self.x + offset_x, self.y + offset_y), 
                              self.size//2)
        
        # Draw dirt/island on top
        pygame.draw.ellipse(surface, self.dirt_color, 
                          (self.x - self.size//2, self.y - self.size//4, 
                           self.size, self.size//2))
        
        # Draw grass
        pygame.draw.ellipse(surface, (100, 200, 100), 
                          (self.x - self.size//2, self.y - self.size//4 - 5, 
                           self.size, self.size//2), 5)

class Building(BackgroundElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = (200, 200, 200)  # Gray for buildings
        self.window_color = (255, 255, 200)  # Yellow for windows
    
    def draw(self, surface):
        # Draw building
        pygame.draw.rect(surface, self.color, 
                        (self.x - self.width//2, self.y - self.height, 
                         self.width, self.height))
        
        # Draw windows
        window_size = min(10, self.width // 5)
        for row in range(self.height // (window_size*2)):
            for col in range(self.width // (window_size*2)):
                pygame.draw.rect(surface, self.window_color, 
                                (self.x - self.width//2 + col*window_size*2 + window_size//2, 
                                 self.y - self.height + row*window_size*2 + window_size//2, 
                                 window_size, window_size))

class Canal(BackgroundElement):
    def __init__(self, x, y, length, width):
        super().__init__(x, y)
        self.length = length
        self.width = width
        self.color = (0, 100, 200)  # Blue for water
        self.angle = random.uniform(0, math.pi)
    
    def draw(self, surface):
        # Calculate end points
        start_x = self.x - math.cos(self.angle) * self.length/2
        start_y = self.y - math.sin(self.angle) * self.length/2
        end_x = self.x + math.cos(self.angle) * self.length/2
        end_y = self.y + math.sin(self.angle) * self.length/2
        
        # Draw canal
        pygame.draw.line(surface, self.color, 
                        (start_x, start_y), 
                        (end_x, end_y), 
                        self.width)
        
        # Draw ripples
        for _ in range(5):
            offset = random.randint(-self.width//2, self.width//2)
            pos = random.random()
            ripple_x = start_x + (end_x - start_x) * pos + math.sin(self.angle) * offset
            ripple_y = start_y + (end_y - start_y) * pos - math.cos(self.angle) * offset
            
            pygame.draw.circle(surface, (100, 200, 255), 
                              (int(ripple_x), int(ripple_y)), 
                              random.randint(2, 5))

class SpookyTree(BackgroundElement):
    def __init__(self, x, y, height):
        super().__init__(x, y)
        self.height = height
        self.trunk_color = (50, 30, 20)  # Dark brown
        self.branches = []
        
        # Create branches
        self.create_branches(self.x, self.y, -self.height, 0, self.height//4, 3)
    
    def create_branches(self, x, y, dx, dy, length, depth):
        if depth <= 0:
            return
        
        end_x = x + dx
        end_y = y + dy
        
        self.branches.append((x, y, end_x, end_y, length//2))
        
        # Create sub-branches
        angle1 = math.atan2(dy, dx) + random.uniform(0.3, 0.8)
        angle2 = math.atan2(dy, dx) - random.uniform(0.3, 0.8)
        
        length_factor = random.uniform(0.6, 0.8)
        new_length = length * length_factor
        
        self.create_branches(end_x, end_y, 
                           math.cos(angle1) * new_length, 
                           math.sin(angle1) * new_length, 
                           new_length, depth - 1)
        
        self.create_branches(end_x, end_y, 
                           math.cos(angle2) * new_length, 
                           math.sin(angle2) * new_length, 
                           new_length, depth - 1)
    
    def draw(self, surface):
        # Draw trunk
        pygame.draw.rect(surface, self.trunk_color, 
                        (self.x - self.height//8, self.y - self.height//2, 
                         self.height//4, self.height//2))
        
        # Draw branches
        for x1, y1, x2, y2, width in self.branches:
            pygame.draw.line(surface, self.trunk_color, 
                            (x1, y1), 
                            (x2, y2), 
                            max(1, width//2))

class FogPatch(BackgroundElement):
    def __init__(self, x, y, size):
        super().__init__(x, y)
        self.size = size
        self.color = (200, 200, 200, 100)  # Semi-transparent gray
        self.particles = []
        
        # Create fog particles
        for _ in range(20):
            self.particles.append({
                'x': self.x + random.uniform(-self.size/2, self.size/2),
                'y': self.y + random.uniform(-self.size/2, self.size/2),
                'size': random.randint(20, 50),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.2, 0.2)
            })
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Wrap around if out of bounds
            if particle['x'] > self.x + self.size/2:
                particle['x'] = self.x - self.size/2
            elif particle['x'] < self.x - self.size/2:
                particle['x'] = self.x + self.size/2
            
            if particle['y'] > self.y + self.size/2:
                particle['y'] = self.y - self.size/2
            elif particle['y'] < self.y - self.size/2:
                particle['y'] = self.y + self.size/2
    
    def draw(self, surface):
        # Create a surface with alpha for transparency
        s = pygame.Surface((800, 600), pygame.SRCALPHA)
        
        # Draw fog particles
        for particle in self.particles:
            pygame.draw.circle(s, self.color, 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])
        
        surface.blit(s, (0, 0))

class MarineHQ(BackgroundElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.building_color = (220, 220, 220)  # Light gray
        self.roof_color = (50, 50, 150)  # Navy blue
    
    def draw(self, surface):
        # Draw main building
        pygame.draw.rect(surface, self.building_color, 
                        (self.x - self.width//2, self.y - self.height, 
                         self.width, self.height))
        
        # Draw roof
        pygame.draw.polygon(surface, self.roof_color, [
            (self.x - self.width//2, self.y - self.height),
            (self.x + self.width//2, self.y - self.height),
            (self.x, self.y - self.height - self.height//3)
        ])
        
        # Draw marine symbol
        symbol_size = min(self.width, self.height) // 4
        pygame.draw.circle(surface, (0, 0, 100), 
                          (self.x, self.y - self.height//2), 
                          symbol_size)
        pygame.draw.circle(surface, (255, 255, 255), 
                          (self.x, self.y - self.height//2), 
                          symbol_size - 5)
        
        # Draw "MARINE" text
        font = pygame.font.Font(None, 36)
        text = font.render("MARINE", True, (0, 0, 100))
        surface.blit(text, (self.x - text.get_width()//2, 
                           self.y - self.height//2 - text.get_height()//2))

class Ship(BackgroundElement):
    def __init__(self, x, y, size, color):
        super().__init__(x, y)
        self.size = size
        self.color = color
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = random.uniform(0.2, 0.5)
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Wrap around if out of bounds
        if self.x < -self.size:
            self.x = 800 + self.size
        elif self.x > 800 + self.size:
            self.x = -self.size
        
        if self.y < -self.size:
            self.y = 600 + self.size
        elif self.y > 600 + self.size:
            self.y = -self.size
    
    def draw(self, surface):
        # Draw ship hull
        pygame.draw.ellipse(surface, self.color, 
                          (self.x - self.size, self.y - self.size//2, 
                           self.size*2, self.size))
        
        # Draw sail
        sail_height = self.size * 1.5
        pygame.draw.rect(surface, (255, 255, 255), 
                        (self.x - self.size//4, self.y - sail_height, 
                         self.size//2, sail_height))
        
        # Draw mast
        pygame.draw.rect(surface, (139, 69, 19), 
                        (self.x - 2, self.y - sail_height, 
                         4, sail_height))
