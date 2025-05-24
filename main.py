import pygame
import sys
import random
import math
from pygame import mixer

# Import custom modules
try:
    from crew_members import *
    from special_attacks import *
    from power_ups import *
    from bosses import *
    from islands import *
except ImportError:
    print("Warning: Some custom modules could not be imported.")

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luffy's Grand Adventure")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
STRAW_HAT_RED = (255, 50, 50)
LUFFY_SKIN = (255, 204, 153)
LUFFY_BLUE = (0, 102, 204)
LUFFY_VEST_RED = (255, 0, 0)
LUFFY_YELLOW = (255, 255, 0)
OCEAN_BLUE = (0, 105, 148)
YELLOW = (255, 255, 0)

# Game states
SPLASH = 0
PLAYING = 1
GAME_OVER = 2
DIFFICULTY_SELECT = 3
PAUSED = 4
CREW_SELECTION = 5

# Game variables
score = 0
game_state = SPLASH
clock = pygame.time.Clock()
FPS = 60
difficulty = "MEDIUM"  # Default difficulty
current_island = 0
islands = ["East Blue", "Alabasta", "Skypiea", "Water 7", "Thriller Bark", "Marineford"]
island_backgrounds = []  # Will store background colors/images for each island
crew_members = []  # Will store unlocked crew members
active_crew_member = None  # Currently active supporting crew member
boss_battle = False
boss = None
power_ups = []
special_attacks = []
boss_attacks = []
message = ""
message_timer = 0
gear_fourth_active = False
gear_fourth_time = 0
paused = False

# Font setup
pygame.font.init()
try:
    title_font = pygame.font.Font(None, 72)
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    tiny_font = pygame.font.Font(None, 24)
except:
    title_font = pygame.font.SysFont('Arial', 72)
    font = pygame.font.SysFont('Arial', 48)
    small_font = pygame.font.SysFont('Arial', 32)
    tiny_font = pygame.font.SysFont('Arial', 24)

class Luffy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 35  # Increased size
        self.skin_color = LUFFY_SKIN
        self.hat_color = STRAW_HAT_RED
        self.vest_color = LUFFY_VEST_RED
        self.cooldown = 0
        self.max_cooldown = 8  # Faster punches
        self.special_cooldown = 0
        self.max_special_cooldown = 240  # 4 seconds cooldown
        self.has_devil_fruit = True
        self.scar_under_eye = True
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_max_time = 60  # 1 second to continue combo
        self.current_attack = 0  # 0: normal punch, 1: gatling, 2: bazooka, 3: rifle
        
        # Animation variables
        self.frame = 0
        self.animation_speed = 0.1
        
        # For sprite-based implementation (future)
        self.sprite = None
    
    def draw(self, surface):
        # Animate slight bobbing
        bob = math.sin(self.frame) * 3
        self.frame += self.animation_speed
        
        # Check if in Gear Fourth mode
        if gear_fourth_active:
            self.draw_gear_fourth(surface, bob)
        else:
            self.draw_normal(surface, bob)
        
        # Draw cooldown indicators
        if self.special_cooldown > 0:
            cooldown_percent = self.special_cooldown / self.max_special_cooldown
            pygame.draw.rect(surface, RED, (self.x - 30, self.y - self.radius*2 - 20 + bob, 60, 10))
            pygame.draw.rect(surface, GREEN, (self.x - 30, self.y - self.radius*2 - 20 + bob, 
                                            60 * (1 - cooldown_percent), 10))
            gear_text = small_font.render("GEAR", True, WHITE)
            surface.blit(gear_text, (self.x - gear_text.get_width()//2, self.y - self.radius*2 - 40 + bob))
        
        # Draw combo counter if active
        if self.combo_count > 0 and self.combo_timer > 0:
            combo_text = small_font.render(f"{self.combo_count} Hit Combo!", True, YELLOW)
            surface.blit(combo_text, (self.x - combo_text.get_width()//2, self.y - self.radius*2 - 70 + bob))
    
    def draw_normal(self, surface, bob):
        # Draw Luffy's legs
        pygame.draw.rect(surface, BLUE, 
                        (self.x - self.radius//1.5, self.y + self.radius//2, 
                         self.radius//1.5, self.radius*1.2))
        pygame.draw.rect(surface, BLUE, 
                        (self.x, self.y + self.radius//2, 
                         self.radius//1.5, self.radius*1.2))
        
        # Draw Luffy's body/torso
        pygame.draw.circle(surface, self.skin_color, (self.x, self.y + bob), self.radius)
        
        # Draw Luffy's red vest - more detailed
        vest_rect = pygame.Rect(self.x - self.radius, self.y - self.radius + bob, 
                               self.radius * 2, self.radius * 2)
        pygame.draw.arc(surface, self.vest_color, vest_rect,
                       math.pi/4, math.pi*7/4, self.radius//1)
        
        # Draw vest details - yellow buttons
        for i in range(3):
            button_y = self.y + (i - 1) * self.radius//2 + bob
            pygame.draw.circle(surface, LUFFY_YELLOW, (self.x, button_y), 4)
        
        # Draw Luffy's neck
        pygame.draw.rect(surface, self.skin_color, 
                        (self.x - self.radius//4, self.y - self.radius//2 + bob, 
                         self.radius//2, self.radius//2))
        
        # Draw Luffy's head
        pygame.draw.circle(surface, self.skin_color, 
                          (self.x, self.y - self.radius//1.2 + bob), self.radius)
        
        # Draw Luffy's straw hat
        hat_y = self.y - self.radius*1.5 + bob
        pygame.draw.ellipse(surface, LUFFY_YELLOW, 
                          (self.x - self.radius*1.3, hat_y - self.radius//2, 
                           self.radius*2.6, self.radius))
        pygame.draw.circle(surface, self.hat_color, 
                          (self.x, hat_y), self.radius - 5)
        pygame.draw.rect(surface, self.hat_color, 
                        (self.x - self.radius - 10, hat_y - 2, 
                         (self.radius + 5) * 2, 5))
        
        # Draw hat string
        pygame.draw.line(surface, BROWN, 
                        (self.x, hat_y + self.radius//2), 
                        (self.x, self.y - self.radius//4 + bob), 3)
        
        # Draw Luffy's face
        # Eyes
        eye_offset = self.radius * 0.4
        pygame.draw.circle(surface, WHITE, 
                          (self.x - eye_offset, self.y - self.radius//1.2 + bob), 8)
        pygame.draw.circle(surface, WHITE, 
                          (self.x + eye_offset, self.y - self.radius//1.2 + bob), 8)
        pygame.draw.circle(surface, BLACK, 
                          (self.x - eye_offset, self.y - self.radius//1.2 + bob), 4)
        pygame.draw.circle(surface, BLACK, 
                          (self.x + eye_offset, self.y - self.radius//1.2 + bob), 4)
        
        # Scar under eye
        if self.scar_under_eye:
            pygame.draw.line(surface, RED, 
                           (self.x - eye_offset - 8, self.y - self.radius//1.5 + bob), 
                           (self.x - eye_offset + 8, self.y - self.radius//1.5 + bob), 4)
        
        # Luffy's smile
        smile_rect = pygame.Rect(self.x - self.radius//2, self.y - self.radius//1.2 + self.radius//3 + bob, 
                                self.radius, self.radius//3)
        pygame.draw.arc(surface, BLACK, smile_rect, 0, math.pi, 3)
        
        # Draw arms
        arm_width = self.radius // 2
        pygame.draw.line(surface, self.skin_color, 
                        (self.x - self.radius, self.y + bob), 
                        (self.x - self.radius*1.5, self.y + self.radius//2 + bob), arm_width)
        pygame.draw.line(surface, self.skin_color, 
                        (self.x + self.radius, self.y + bob), 
                        (self.x + self.radius*1.5, self.y + self.radius//2 + bob), arm_width)
        
        # Draw hands
        pygame.draw.circle(surface, self.skin_color, 
                          (self.x - self.radius*1.5, self.y + self.radius//2 + bob), arm_width)
        pygame.draw.circle(surface, self.skin_color, 
                          (self.x + self.radius*1.5, self.y + self.radius//2 + bob), arm_width)
    
    def draw_gear_fourth(self, surface, bob):
        # Draw Luffy's legs - larger in Gear Fourth
        pygame.draw.rect(surface, BLUE, 
                        (self.x - self.radius//1.2, self.y + self.radius//2, 
                         self.radius//1.2, self.radius*1.5))
        pygame.draw.rect(surface, BLUE, 
                        (self.x, self.y + self.radius//2, 
                         self.radius//1.2, self.radius*1.5))
        
        # Draw Luffy's body/torso - larger and with haki pattern
        pygame.draw.circle(surface, (50, 0, 0), (self.x, self.y + bob), self.radius * 1.3)
        
        # Draw haki pattern
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius)
            size = random.uniform(3, 8)
            
            pattern_x = self.x + math.cos(angle) * distance
            pattern_y = self.y + bob + math.sin(angle) * distance
            
            pygame.draw.circle(surface, BLACK, 
                              (int(pattern_x), int(pattern_y)), 
                              int(size))
        
        # Draw Luffy's red vest - torn in Gear Fourth
        vest_rect = pygame.Rect(self.x - self.radius*1.3, self.y - self.radius*1.3 + bob, 
                               self.radius * 2.6, self.radius * 2.6)
        pygame.draw.arc(surface, self.vest_color, vest_rect,
                       math.pi/4, math.pi*7/4, self.radius//1)
        
        # Draw Luffy's neck - thicker
        pygame.draw.rect(surface, (50, 0, 0), 
                        (self.x - self.radius//3, self.y - self.radius//2 + bob, 
                         self.radius//1.5, self.radius//2))
        
        # Draw Luffy's head - with haki
        pygame.draw.circle(surface, (50, 0, 0), 
                          (self.x, self.y - self.radius//1.2 + bob), self.radius*1.2)
        
        # Draw Luffy's straw hat
        hat_y = self.y - self.radius*1.8 + bob
        pygame.draw.ellipse(surface, LUFFY_YELLOW, 
                          (self.x - self.radius*1.3, hat_y - self.radius//2, 
                           self.radius*2.6, self.radius))
        pygame.draw.circle(surface, self.hat_color, 
                          (self.x, hat_y), self.radius - 5)
        pygame.draw.rect(surface, self.hat_color, 
                        (self.x - self.radius - 10, hat_y - 2, 
                         (self.radius + 5) * 2, 5))
        
        # Draw hat string
        pygame.draw.line(surface, BROWN, 
                        (self.x, hat_y + self.radius//2), 
                        (self.x, self.y - self.radius//4 + bob), 3)
        
        # Draw Luffy's face - angry in Gear Fourth
        # Eyes
        eye_offset = self.radius * 0.5
        pygame.draw.circle(surface, WHITE, 
                          (self.x - eye_offset, self.y - self.radius//1.2 + bob), 10)
        pygame.draw.circle(surface, WHITE, 
                          (self.x + eye_offset, self.y - self.radius//1.2 + bob), 10)
        pygame.draw.circle(surface, BLACK, 
                          (self.x - eye_offset, self.y - self.radius//1.2 + bob), 5)
        pygame.draw.circle(surface, BLACK, 
                          (self.x + eye_offset, self.y - self.radius//1.2 + bob), 5)
        
        # Scar under eye
        if self.scar_under_eye:
            pygame.draw.line(surface, RED, 
                           (self.x - eye_offset - 10, self.y - self.radius//1.5 + bob), 
                           (self.x - eye_offset + 10, self.y - self.radius//1.5 + bob), 5)
        
        # Luffy's angry mouth
        pygame.draw.line(surface, BLACK, 
                        (self.x - self.radius//2, self.y - self.radius//1.2 + self.radius//2 + bob), 
                        (self.x + self.radius//2, self.y - self.radius//1.2 + self.radius//2 + bob), 3)
        
        # Draw steam effects
        for _ in range(10):
            offset_x = random.randint(-self.radius*2, self.radius*2)
            offset_y = random.randint(-self.radius*2, self.radius*2)
            if offset_x**2 + offset_y**2 <= (self.radius*2)**2:
                steam_size = random.randint(5, 15)
                pygame.draw.circle(surface, (255, 255, 255, 100), 
                                  (int(self.x + offset_x), int(self.y + offset_y + bob)), 
                                  steam_size)
        
        # Draw arms - larger and with haki
        arm_width = self.radius // 1.5
        pygame.draw.line(surface, (50, 0, 0), 
                        (self.x - self.radius*1.3, self.y + bob), 
                        (self.x - self.radius*2, self.y + self.radius//2 + bob), arm_width)
        pygame.draw.line(surface, (50, 0, 0), 
                        (self.x + self.radius*1.3, self.y + bob), 
                        (self.x + self.radius*2, self.y + self.radius//2 + bob), arm_width)
        
        # Draw hands - larger
        pygame.draw.circle(surface, (50, 0, 0), 
                          (self.x - self.radius*2, self.y + self.radius//2 + bob), arm_width*1.2)
        pygame.draw.circle(surface, (50, 0, 0), 
                          (self.x + self.radius*2, self.y + self.radius//2 + bob), arm_width*1.2)
    
    def update(self):
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0

class Pirate:
    def __init__(self):
        # Randomly determine which edge the pirate will spawn from
        edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        self.size = random.randint(15, 25)
        
        # Adjust pirate parameters based on difficulty
        if difficulty == "EASY":
            self.speed = random.uniform(0.5, 1.2)
            self.health = random.randint(1, 2)
            devil_fruit_chance = 0.05  # 5% chance
        elif difficulty == "MEDIUM":
            self.speed = random.uniform(0.8, 1.8)
            self.health = random.randint(1, 2)
            devil_fruit_chance = 0.15  # 15% chance
        else:  # HARD
            self.speed = random.uniform(1.0, 2.2)
            self.health = random.randint(1, 3)
            devil_fruit_chance = 0.25  # 25% chance
        
        # Check if there are already strong pirates on screen
        global pirates
        strong_pirates_exist = False
        for p in pirates:
            if p.has_devil_fruit:
                strong_pirates_exist = True
                break
        
        # If strong pirates exist and score is low, don't spawn another strong pirate
        if strong_pirates_exist and score < 10:
            self.has_devil_fruit = False
        else:
            self.has_devil_fruit = random.random() < devil_fruit_chance
        
        # Determine pirate type and color
        if self.has_devil_fruit:
            pirate_types = ["logia", "paramecia", "zoan"]
            weights = [0.33, 0.33, 0.34]
            self.type = random.choices(pirate_types, weights=weights)[0]
        else:
            self.type = "normal"
        
        if self.type == "normal":
            self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        elif self.type == "logia":
            self.color = (255, random.randint(100, 200), 0)  # Orange/fire-like
            self.health += 1
        elif self.type == "paramecia":
            self.color = (random.randint(100, 200), 0, random.randint(100, 200))  # Purple-ish
            self.speed *= 1.2  # Reduced speed boost
        elif self.type == "zoan":
            self.color = (0, random.randint(100, 150), 0)  # Green-ish
            self.size += 10
            self.health += 1  # Reduced health boost
        
        if edge == 0:  # Top edge
            self.x = random.randint(0, WIDTH)
            self.y = 0
        elif edge == 1:  # Right edge
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT)
        elif edge == 2:  # Bottom edge
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT
        else:  # Left edge
            self.x = 0
            self.y = random.randint(0, HEIGHT)
        
        # Calculate direction vector towards Luffy
        dx = WIDTH // 2 - self.x
        dy = HEIGHT // 2 - self.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        self.dx = dx / distance * self.speed
        self.dy = dy / distance * self.speed
        
        # Animation variables
        self.frame = 0
        self.animation_speed = 0.2
        self.walk_cycle = 0
        
        # Status effects
        self.immobilized = False
        self.immobilize_time = 0
        self.frozen = False
        self.freeze_time = 0
    
    def update(self):
        # Check status effects
        if self.immobilized:
            self.immobilize_time -= 1
            if self.immobilize_time <= 0:
                self.immobilized = False
            return
        
        if self.frozen:
            self.freeze_time -= 1
            if self.freeze_time <= 0:
                self.frozen = False
            return
        
        # Normal movement
        self.x += self.dx
        self.y += self.dy
        
        # Update animation
        self.frame += self.animation_speed
        self.walk_cycle = int(self.frame) % 4
    
    def draw(self, surface):
        # Draw pirate body with slight bobbing based on walk cycle
        bob_offset = math.sin(self.frame * math.pi) * 2
        
        # If frozen, draw ice effect
        if self.frozen:
            pygame.draw.circle(surface, (150, 200, 255), 
                              (int(self.x), int(self.y + bob_offset)), 
                              self.size + 5)
        
        # Draw pirate body
        pygame.draw.circle(surface, self.color, 
                          (int(self.x), int(self.y + bob_offset)), self.size)
        
        # Draw pirate features based on type
        if self.type == "normal":
            # Draw pirate hat
            hat_width = self.size * 2
            hat_height = self.size * 0.8
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - hat_width//2, self.y - self.size - hat_height//2 + bob_offset, 
                               hat_width, hat_height))
            
            # Draw skull and crossbones on hat
            skull_size = hat_height * 0.6
            pygame.draw.circle(surface, WHITE, 
                              (int(self.x), int(self.y - self.size + bob_offset)), 
                              int(skull_size))
            
        elif self.type == "logia":
            # Draw fire-like effect
            for _ in range(8):
                offset_x = random.randint(-self.size//2, self.size//2)
                offset_y = random.randint(-self.size//2, self.size//2)
                flame_size = random.randint(self.size//3, self.size//2)
                pygame.draw.circle(surface, (255, 255, 0), 
                                  (int(self.x + offset_x), int(self.y + offset_y + bob_offset)), 
                                  flame_size)
            
            # Draw logia user face
            pygame.draw.circle(surface, (255, 200, 150), 
                              (int(self.x), int(self.y + bob_offset)), 
                              int(self.size * 0.7))
            
        elif self.type == "paramecia":
            # Draw special ability indicator - weird body shape
            for i in range(3):
                offset = self.size * 0.6
                angle = self.frame * 0.2 + i * (2 * math.pi / 3)
                blob_x = self.x + math.cos(angle) * offset
                blob_y = self.y + math.sin(angle) * offset + bob_offset
                pygame.draw.circle(surface, (255, 0, 255), 
                                  (int(blob_x), int(blob_y)), 
                                  int(self.size * 0.6))
            
        elif self.type == "zoan":
            # Draw animal features - horns or claws
            horn_length = self.size * 0.8
            
            pygame.draw.polygon(surface, (0, 100, 0), 
                              [(self.x, self.y - self.size + bob_offset), 
                               (self.x - self.size//2, self.y - self.size - horn_length + bob_offset),
                               (self.x + self.size//2, self.y - self.size - horn_length + bob_offset)])
            
            # Draw beast-like teeth
            teeth_width = self.size * 0.8
            teeth_height = self.size * 0.3
            pygame.draw.rect(surface, WHITE, 
                           (self.x - teeth_width//2, self.y + bob_offset, 
                            teeth_width, teeth_height))
            
            # Draw teeth lines
            for i in range(1, 4):
                line_x = self.x - teeth_width//2 + i * teeth_width//4
                pygame.draw.line(surface, BLACK, 
                               (line_x, self.y + bob_offset),
                               (line_x, self.y + teeth_height + bob_offset), 2)
        
        # Draw eyes for all pirates
        eye_size = max(3, self.size // 4)
        eye_offset = self.size * 0.4
        
        # Left eye
        pygame.draw.circle(surface, WHITE, 
                          (int(self.x - eye_offset), int(self.y - self.size/3 + bob_offset)), 
                          eye_size)
        pygame.draw.circle(surface, BLACK, 
                          (int(self.x - eye_offset), int(self.y - self.size/3 + bob_offset)), 
                          eye_size//2)
        
        # Right eye
        pygame.draw.circle(surface, WHITE, 
                          (int(self.x + eye_offset), int(self.y - self.size/3 + bob_offset)), 
                          eye_size)
        pygame.draw.circle(surface, BLACK, 
                          (int(self.x + eye_offset), int(self.y - self.size/3 + bob_offset)), 
                          eye_size//2)
        
        # Draw angry eyebrows
        pygame.draw.line(surface, BLACK, 
                        (self.x - eye_offset - eye_size, self.y - self.size/2 - eye_size/2 + bob_offset),
                        (self.x - eye_offset + eye_size, self.y - self.size/2 + bob_offset), 2)
        pygame.draw.line(surface, BLACK, 
                        (self.x + eye_offset - eye_size, self.y - self.size/2 + bob_offset),
                        (self.x + eye_offset + eye_size, self.y - self.size/2 - eye_size/2 + bob_offset), 2)
        
        # Draw health indicator
        for i in range(int(self.health)):
            pygame.draw.circle(surface, RED, 
                              (int(self.x - self.size + i*10), int(self.y - self.size - 15)), 4)
        
        # Draw immobilized indicator
        if self.immobilized:
            pygame.draw.line(surface, (255, 0, 0), 
                            (self.x - self.size, self.y - self.size - 25),
                            (self.x + self.size, self.y - self.size - 25), 3)
    
    def collides_with_luffy(self, luffy):
        distance = math.sqrt((self.x - luffy.x) ** 2 + (self.y - luffy.y) ** 2)
        return distance < (self.size + luffy.radius)

class RubberPunch:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.life = 20  # Punch disappears after 20 frames
        self.active = True
        self.fist_size = 20
        self.fist_color = LUFFY_SKIN
        
        # Calculate direction vector
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
        self.extending = True  # True when extending, False when retracting
        self.extension_speed = 25
        self.current_fist_x = start_x
        self.current_fist_y = start_y
        
        # Visual effect variables
        self.stretch_points = []
        for i in range(5):
            self.stretch_points.append(random.uniform(0.1, 0.9))
        self.stretch_points.sort()
    
    def update(self):
        if self.extending:
            # Extend the punch
            self.current_length = min(self.current_length + self.extension_speed, self.max_length)
            if self.current_length >= self.max_length:
                self.extending = False
        else:
            # Retract the punch
            self.current_length = max(self.current_length - self.extension_speed, 0)
            if self.current_length <= 0:
                self.active = False
        
        # Update fist position
        self.current_fist_x = self.start_x + self.dx * self.current_length
        self.current_fist_y = self.start_y + self.dy * self.current_length
    
    def draw(self, surface):
        # Draw stretching arm with bulges to show rubber effect
        last_x, last_y = self.start_x, self.start_y
        
        for i, point in enumerate(self.stretch_points):
            # Calculate position along the arm
            pos_x = self.start_x + self.dx * self.current_length * point
            pos_y = self.start_y + self.dy * self.current_length * point
            
            # Draw segment
            pygame.draw.line(surface, self.fist_color, (last_x, last_y), (pos_x, pos_y), 12)
            
            # Draw bulge at joint
            bulge_size = 8 if i % 2 == 0 else 6
            pygame.draw.circle(surface, self.fist_color, (int(pos_x), int(pos_y)), bulge_size)
            
            last_x, last_y = pos_x, pos_y
        
        # Draw final segment
        pygame.draw.line(surface, self.fist_color, (last_x, last_y), 
                         (self.current_fist_x, self.current_fist_y), 12)
        
        # Draw fist
        pygame.draw.circle(surface, self.fist_color, 
                          (int(self.current_fist_x), int(self.current_fist_y)), self.fist_size)
        
        # Draw knuckles
        knuckle_offset = self.fist_size * 0.5
        for i in range(4):
            angle = math.atan2(self.dy, self.dx) + math.pi/2
            offset_x = math.cos(angle) * (i - 1.5) * knuckle_offset * 0.5
            offset_y = math.sin(angle) * (i - 1.5) * knuckle_offset * 0.5
            pygame.draw.circle(surface, (220, 170, 130),  # Slightly darker skin for knuckles
                              (int(self.current_fist_x + offset_x), 
                               int(self.current_fist_y + offset_y)), 4)
    
    def collides_with_pirate(self, pirate):
        # Check if the fist hits the pirate
        distance = math.sqrt((self.current_fist_x - pirate.x)**2 + (self.current_fist_y - pirate.y)**2)
        return distance < (self.fist_size + pirate.size)

class GearSecond:
    def __init__(self, luffy_x, luffy_y):
        self.x = luffy_x
        self.y = luffy_y
        self.radius = 200
        self.life = 240  # 4 seconds at 60 FPS
        self.active = True
        self.color = (255, 100, 100, 100)  # Red with transparency
        self.steam_particles = []
        
        # Create initial steam particles
        for _ in range(30):
            self.add_steam_particle()
    
    def add_steam_particle(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, self.radius)
        speed = random.uniform(1, 3)
        size = random.uniform(5, 15)
        lifetime = random.randint(20, 60)
        
        self.steam_particles.append({
            'x': self.x + math.cos(angle) * distance,
            'y': self.y + math.sin(angle) * distance,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.active = False
        
        # Add new steam particles
        if random.random() < 0.3:
            self.add_steam_particle()
        
        # Update steam particles
        for particle in self.steam_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.steam_particles.remove(particle)
    
    def draw(self, surface):
        # Create a surface with alpha for transparency
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))
        
        # Draw steam particles
        for particle in self.steam_particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = (255, 255, 255, alpha)
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                              (int(particle['size']), int(particle['size'])), 
                              int(particle['size']))
            
            surface.blit(particle_surface, 
                        (int(particle['x'] - particle['size']), 
                         int(particle['y'] - particle['size'])))
        
        # Draw "GEAR SECOND" text
        if self.life > 200:  # Only show text at the beginning
            text = title_font.render("GEAR SECOND!", True, RED)
            text_shadow = title_font.render("GEAR SECOND!", True, BLACK)
            
            # Draw shadow
            surface.blit(text_shadow, (self.x - text.get_width()//2 + 3, self.y - 100 + 3))
            # Draw text
            surface.blit(text, (self.x - text.get_width()//2, self.y - 100))
    
    def collides_with_pirate(self, pirate):
        distance = math.sqrt((self.x - pirate.x)**2 + (self.y - pirate.y)**2)
        return distance < self.radius

def draw_splash_screen():
    # Draw ocean background
    for y in range(0, HEIGHT, 20):
        wave_height = math.sin(pygame.time.get_ticks() * 0.001 + y * 0.1) * 5
        color_value = max(50, min(150, 100 + wave_height * 5))
        pygame.draw.rect(surface=screen, 
                        color=(0, color_value, min(255, color_value + 100)), 
                        rect=(0, y, WIDTH, 20))
    
    # Draw title with shadow effect
    title = title_font.render("Luffy's Grand Adventure", True, STRAW_HAT_RED)
    title_shadow = title_font.render("Luffy's Grand Adventure", True, BLACK)
    
    screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 4, HEIGHT//2 - 120 + 4))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
    
    subtitle = font.render("Defeat the pirates with your rubber powers!", True, WHITE)
    subtitle_shadow = font.render("Defeat the pirates with your rubber powers!", True, BLACK)
    
    screen.blit(subtitle_shadow, (WIDTH//2 - subtitle.get_width()//2 + 2, HEIGHT//2 - 50 + 2))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 50))
    
    instruction = small_font.render("Click to Select Difficulty", True, WHITE)
    screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 20))
    
    # Draw One Piece logo-inspired decoration
    skull_size = 60
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2 + 100), skull_size)
    pygame.draw.circle(screen, BLACK, (WIDTH//2 - skull_size//3, HEIGHT//2 + 90), skull_size//5)
    pygame.draw.circle(screen, BLACK, (WIDTH//2 + skull_size//3, HEIGHT//2 + 90), skull_size//5)
    
    # Draw straw hat on skull
    pygame.draw.ellipse(screen, STRAW_HAT_RED, 
                      (WIDTH//2 - skull_size, HEIGHT//2 + 100 - skull_size, 
                       skull_size*2, skull_size//2))
    
    # Draw crossbones
    bone_length = skull_size * 1.2
    bone_width = skull_size // 6
    
    # First bone
    pygame.draw.line(screen, WHITE, 
                    (WIDTH//2 - bone_length//2, HEIGHT//2 + 100 + bone_length//2),
                    (WIDTH//2 + bone_length//2, HEIGHT//2 + 100 - bone_length//2),
                    bone_width)
    
    # Second bone
    pygame.draw.line(screen, WHITE, 
                    (WIDTH//2 - bone_length//2, HEIGHT//2 + 100 - bone_length//2),
                    (WIDTH//2 + bone_length//2, HEIGHT//2 + 100 + bone_length//2),
                    bone_width)

def draw_difficulty_screen():
    # Draw ocean background
    for y in range(0, HEIGHT, 20):
        wave_height = math.sin(pygame.time.get_ticks() * 0.001 + y * 0.1) * 5
        color_value = max(50, min(150, 100 + wave_height * 5))
        pygame.draw.rect(surface=screen, 
                        color=(0, color_value, min(255, color_value + 100)), 
                        rect=(0, y, WIDTH, 20))
    
    title = font.render("Select Difficulty", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    
    # Draw difficulty buttons
    difficulties = ["EASY", "MEDIUM", "HARD"]
    button_width, button_height = 200, 60
    button_y = HEIGHT//2 - button_height//2
    spacing = 30
    
    total_width = len(difficulties) * button_width + (len(difficulties) - 1) * spacing
    start_x = WIDTH//2 - total_width//2
    
    for i, diff in enumerate(difficulties):
        button_x = start_x + i * (button_width + spacing)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check if mouse is over this button
        mouse_pos = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_pos)
        
        # Draw button with appropriate color
        if diff == difficulty:
            # Selected difficulty
            pygame.draw.rect(screen, GREEN, button_rect)
            pygame.draw.rect(screen, WHITE, button_rect, 3)
        elif hover:
            # Hovered difficulty
            pygame.draw.rect(screen, (100, 100, 100), button_rect)
            pygame.draw.rect(screen, WHITE, button_rect, 2)
        else:
            # Normal difficulty
            pygame.draw.rect(screen, (50, 50, 50), button_rect)
            pygame.draw.rect(screen, WHITE, button_rect, 1)
        
        # Draw difficulty text
        diff_text = font.render(diff, True, WHITE)
        screen.blit(diff_text, (button_x + button_width//2 - diff_text.get_width()//2, 
                              button_y + button_height//2 - diff_text.get_height()//2))
    
    # Draw difficulty descriptions
    if difficulty == "EASY":
        desc = "Slower pirates, more health, easier to defeat"
    elif difficulty == "MEDIUM":
        desc = "Balanced gameplay for a moderate challenge"
    else:  # HARD
        desc = "Faster pirates, more devil fruit users, tougher challenge"
    
    desc_text = small_font.render(desc, True, WHITE)
    screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT*3//4))
    
    # Draw start button
    start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT*3//4 + 50, 200, 50)
    pygame.draw.rect(screen, STRAW_HAT_RED, start_button)
    pygame.draw.rect(screen, WHITE, start_button, 2)
    
    start_text = font.render("START", True, WHITE)
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 
                           HEIGHT*3//4 + 50 + 25 - start_text.get_height()//2))
    
    return start_button

def draw_game_over_screen():
    # Draw dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over_text = title_font.render("Game Over", True, RED)
    game_over_shadow = title_font.render("Game Over", True, BLACK)
    
    screen.blit(game_over_shadow, (WIDTH//2 - game_over_text.get_width()//2 + 3, HEIGHT//2 - 120 + 3))
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
    
    score_text = font.render(f"Pirates Defeated: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    
    # Draw buttons
    button_width, button_height = 200, 50
    button_spacing = 30
    
    # Restart button
    restart_button = pygame.Rect(WIDTH//2 - button_width - button_spacing//2, HEIGHT//2 + 70, 
                               button_width, button_height)
    pygame.draw.rect(screen, BLUE, restart_button)
    pygame.draw.rect(screen, WHITE, restart_button, 2)
    
    restart_text = small_font.render("Restart", True, WHITE)
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width()//2, 
                             restart_button.centery - restart_text.get_height()//2))
    
    # Main menu button
    menu_button = pygame.Rect(WIDTH//2 + button_spacing//2, HEIGHT//2 + 70, 
                            button_width, button_height)
    pygame.draw.rect(screen, GREEN, menu_button)
    pygame.draw.rect(screen, WHITE, menu_button, 2)
    
    menu_text = small_font.render("Main Menu", True, WHITE)
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                          menu_button.centery - menu_text.get_height()//2))
    
    return restart_button, menu_button

def draw_pause_menu():
    # Draw dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Draw pause title
    pause_text = title_font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//4))
    
    # Draw buttons
    button_width, button_height = 200, 50
    button_spacing = 20
    
    # Resume button
    resume_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - button_height//2, 
                              button_width, button_height)
    pygame.draw.rect(screen, GREEN, resume_button)
    pygame.draw.rect(screen, WHITE, resume_button, 2)
    
    resume_text = font.render("Resume", True, WHITE)
    screen.blit(resume_text, (resume_button.centerx - resume_text.get_width()//2, 
                            resume_button.centery - resume_text.get_height()//2))
    
    # Crew button
    crew_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + button_height + button_spacing, 
                            button_width, button_height)
    pygame.draw.rect(screen, BLUE, crew_button)
    pygame.draw.rect(screen, WHITE, crew_button, 2)
    
    crew_text = font.render("Crew", True, WHITE)
    screen.blit(crew_text, (crew_button.centerx - crew_text.get_width()//2, 
                          crew_button.centery - crew_text.get_height()//2))
    
    # Main menu button
    menu_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 2*(button_height + button_spacing), 
                            button_width, button_height)
    pygame.draw.rect(screen, RED, menu_button)
    pygame.draw.rect(screen, WHITE, menu_button, 2)
    
    menu_text = font.render("Main Menu", True, WHITE)
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width()//2, 
                          menu_button.centery - menu_text.get_height()//2))
    
    return resume_button, crew_button, menu_button

def draw_crew_selection():
    # Draw dark background
    screen.fill((20, 20, 50))
    
    # Draw title
    title_text = title_font.render("Straw Hat Crew", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
    
    # Draw crew members in a grid
    grid_cols = 3
    grid_rows = 3
    cell_width = WIDTH // grid_cols
    cell_height = (HEIGHT - 150) // grid_rows
    
    crew_buttons = []
    
    for i, crew_member in enumerate(crew_members):
        row = i // grid_cols
        col = i % grid_cols
        
        x = col * cell_width + cell_width//2
        y = row * cell_height + 120
        
        # Draw crew member box
        box_rect = pygame.Rect(x - cell_width//2 + 20, y - cell_height//2 + 20, 
                              cell_width - 40, cell_height - 40)
        
        if crew_member.unlocked:
            if crew_member == active_crew_member:
                pygame.draw.rect(screen, (0, 200, 0), box_rect)  # Green for active
            else:
                pygame.draw.rect(screen, (100, 100, 100), box_rect)  # Gray for unlocked
        else:
            pygame.draw.rect(screen, (50, 50, 50), box_rect)  # Dark gray for locked
        
        pygame.draw.rect(screen, WHITE, box_rect, 2)
        
        # Draw crew member name
        name_text = small_font.render(crew_member.name, True, WHITE)
        screen.blit(name_text, (x - name_text.get_width()//2, y - cell_height//2 + 30))
        
        # Draw crew member image or placeholder
        if crew_member.image:
            screen.blit(crew_member.image, (x - 30, y - 20))
        else:
            pygame.draw.circle(screen, (200, 200, 200), (x, y), 30)
        
        # Draw ability name
        if crew_member.unlocked:
            ability_text = tiny_font.render(crew_member.ability_name, True, YELLOW)
            screen.blit(ability_text, (x - ability_text.get_width()//2, y + 40))
        else:
            locked_text = tiny_font.render(f"Unlock at {crew_member.unlock_score} points", True, RED)
            screen.blit(locked_text, (x - locked_text.get_width()//2, y + 40))
        
        crew_buttons.append(box_rect)
    
    # Draw back button
    back_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 70, 200, 50)
    pygame.draw.rect(screen, RED, back_button)
    pygame.draw.rect(screen, WHITE, back_button, 2)
    
    back_text = font.render("Back", True, WHITE)
    screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, 
                          back_button.centery - back_text.get_height()//2))
    
    return crew_buttons, back_button

def reset_game():
    global score, pirates, punches, luffy, game_state, special_moves, special_attacks
    global power_ups, boss_battle, boss, boss_attacks, message, message_timer
    global gear_fourth_active, gear_fourth_time
    
    score = 0
    pirates = []
    punches = []
    special_moves = []
    special_attacks = []
    power_ups = []
    boss_attacks = []
    boss_battle = False
    boss = None
    message = ""
    message_timer = 0
    gear_fourth_active = False
    gear_fourth_time = 0
    
    luffy = Luffy(WIDTH // 2, HEIGHT // 2)
    game_state = PLAYING
    
    # Set game parameters based on difficulty
    global pirate_spawn_interval, pirate_spawn_timer
    pirate_spawn_timer = 0
    
    if difficulty == "EASY":
        pirate_spawn_interval = 120  # 2 seconds between pirates
        luffy.max_special_cooldown = 180  # 3 seconds cooldown
    elif difficulty == "MEDIUM":
        pirate_spawn_interval = 90  # 1.5 seconds between pirates
        luffy.max_special_cooldown = 240  # 4 seconds cooldown
    else:  # HARD
        pirate_spawn_interval = 60  # 1 second between pirates
        luffy.max_special_cooldown = 300  # 5 seconds cooldown

def initialize_game():
    global crew_members, active_crew_member, island_backgrounds
    
    # Create crew members
    crew_members = [
        Zoro(),
        Nami(),
        Usopp(),
        Sanji(),
        Chopper(),
        Robin(),
        Franky(),
        Brook(),
        Jinbe()
    ]
    
    # Initialize island backgrounds
    island_backgrounds = [
        EastBlue(WIDTH, HEIGHT),
        Alabasta(WIDTH, HEIGHT),
        Skypiea(WIDTH, HEIGHT),
        WaterSeven(WIDTH, HEIGHT),
        ThrillerBark(WIDTH, HEIGHT),
        Marineford(WIDTH, HEIGHT)
    ]
    
    # Set up sound effects
    try:
        mixer.init()
        global punch_sound, hit_sound, game_over_sound, gear_second_sound
        punch_sound = mixer.Sound('assets/sounds/punch.wav')
        hit_sound = mixer.Sound('assets/sounds/hit.wav')
        game_over_sound = mixer.Sound('assets/sounds/game_over.wav')
        gear_second_sound = mixer.Sound('assets/sounds/gear_second.wav')
        
        # Set volume
        punch_sound.set_volume(0.5)
        hit_sound.set_volume(0.5)
        game_over_sound.set_volume(0.7)
        gear_second_sound.set_volume(0.7)
        
        # Try to load background music
        mixer.music.load('assets/sounds/one_piece_theme.mp3')
        mixer.music.play(-1)  # Loop indefinitely
        mixer.music.set_volume(0.3)
        
        global sounds_loaded
        sounds_loaded = True
    except:
        # global sounds_loaded
        sounds_loaded = False
        print("Could not load sounds. Game will run without audio.")

# Initialize game objects
luffy = Luffy(WIDTH // 2, HEIGHT // 2)
pirates = []
punches = []
special_moves = []
special_attacks = []
boss_attacks = []
pirate_spawn_timer = 0
pirate_spawn_interval = 60  # Default, will be adjusted based on difficulty
sounds_loaded = False

# Background elements
def create_clouds():
    clouds = []
    for _ in range(10):
        cloud = {
            'x': random.randint(-100, WIDTH + 100),
            'y': random.randint(20, HEIGHT//3),
            'width': random.randint(80, 200),
            'height': random.randint(40, 80),
            'speed': random.uniform(0.2, 0.8)
        }
        clouds.append(cloud)
    return clouds

clouds = create_clouds()

# Try to initialize game
try:
    initialize_game()
except Exception as e:
    print(f"Error initializing game: {e}")
    # Continue with minimal initialization
    crew_members = []
    island_backgrounds = []
    sounds_loaded = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and game_state == PLAYING:
                paused = not paused
            elif event.key == pygame.K_e and game_state == PLAYING and not paused:
                # Use active crew member ability
                if active_crew_member and active_crew_member.unlocked:
                    if active_crew_member.current_cooldown <= 0:
                        game_state_data = {
                            'luffy': luffy,
                            'pirates': pirates,
                            'special_attacks': special_attacks,
                            'score': score
                        }
                        result = active_crew_member.use_ability(game_state_data)
                        if result:
                            message = result
                            message_timer = 180  # 3 seconds
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game_state == SPLASH:
                game_state = DIFFICULTY_SELECT
            
            elif game_state == DIFFICULTY_SELECT:
                # Check difficulty buttons
                button_width, button_height = 200, 60
                button_y = HEIGHT//2 - button_height//2
                spacing = 30
                
                difficulties = ["EASY", "MEDIUM", "HARD"]
                total_width = len(difficulties) * button_width + (len(difficulties) - 1) * spacing
                start_x = WIDTH//2 - total_width//2
                
                for i, diff in enumerate(difficulties):
                    button_x = start_x + i * (button_width + spacing)
                    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                    
                    if button_rect.collidepoint(mouse_pos):
                        difficulty = diff
                
                # Check start button
                start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT*3//4 + 50, 200, 50)
                if start_button.collidepoint(mouse_pos):
                    reset_game()
            
            elif game_state == PLAYING and not paused:
                # Left click for normal punch
                if event.button == 1 and luffy.cooldown <= 0:
                    punches.append(RubberPunch(luffy.x, luffy.y, mouse_pos[0], mouse_pos[1]))
                    luffy.cooldown = luffy.max_cooldown
                    if sounds_loaded:
                        punch_sound.play()
                # Right click for special move (Gear Second)
                elif event.button == 3 and luffy.special_cooldown <= 0:
                    special_moves.append(GearSecond(luffy.x, luffy.y))
                    luffy.special_cooldown = luffy.max_special_cooldown
                    if sounds_loaded:
                        gear_second_sound.play()
            
            elif game_state == GAME_OVER:
                restart_button = pygame.Rect(WIDTH//2 - 200 - 15, HEIGHT//2 + 70, 200, 50)
                menu_button = pygame.Rect(WIDTH//2 + 15, HEIGHT//2 + 70, 200, 50)
                
                if restart_button.collidepoint(mouse_pos):
                    reset_game()
                elif menu_button.collidepoint(mouse_pos):
                    game_state = SPLASH
            
            elif game_state == PAUSED:
                resume_button, crew_button, menu_button = draw_pause_menu()
                
                if resume_button.collidepoint(mouse_pos):
                    paused = False
                elif crew_button.collidepoint(mouse_pos):
                    game_state = CREW_SELECTION
                elif menu_button.collidepoint(mouse_pos):
                    game_state = SPLASH
            
            elif game_state == CREW_SELECTION:
                crew_buttons, back_button = draw_crew_selection()
                
                # Check if a crew member was clicked
                for i, button in enumerate(crew_buttons):
                    if button.collidepoint(mouse_pos) and i < len(crew_members):
                        if crew_members[i].unlocked:
                            active_crew_member = crew_members[i]
                
                # Check if back button was clicked
                if back_button.collidepoint(mouse_pos):
                    game_state = PAUSED
    
    # Clear screen
    screen.fill(OCEAN_BLUE)
    
    if game_state == SPLASH:
        draw_splash_screen()
    
    elif game_state == DIFFICULTY_SELECT:
        start_button = draw_difficulty_screen()
    
    elif game_state == PLAYING:
        if paused:
            # Draw the game in the background
            if island_backgrounds and current_island < len(island_backgrounds):
                island_backgrounds[current_island].draw(screen)
            
            # Draw Luffy
            luffy.draw(screen)
            
            # Draw pause menu over the game
            draw_pause_menu()
        else:
            # Draw background based on current island
            if island_backgrounds and current_island < len(island_backgrounds):
                island_backgrounds[current_island].update()
                island_backgrounds[current_island].draw(screen)
            else:
                # Draw clouds as fallback
                for cloud in clouds:
                    # Move clouds
                    cloud['x'] += cloud['speed']
                    if cloud['x'] > WIDTH + 100:
                        cloud['x'] = -cloud['width']
                        cloud['y'] = random.randint(20, HEIGHT//3)
                    
                    # Draw cloud
                    pygame.draw.ellipse(screen, (230, 230, 230), 
                                      (cloud['x'], cloud['y'], cloud['width'], cloud['height']))
                    pygame.draw.ellipse(screen, (200, 200, 200), 
                                      (cloud['x'] + cloud['width']//4, cloud['y'] + cloud['height']//4, 
                                       cloud['width']//2, cloud['height']//2))
            
            # Update cooldowns
            if luffy.cooldown > 0:
                luffy.cooldown -= 1
            if luffy.special_cooldown > 0:
                luffy.special_cooldown -= 1
            
            # Update crew member cooldowns
            for crew_member in crew_members:
                crew_member.update()
            
            # Update Gear Fourth timer
            if gear_fourth_active:
                gear_fourth_time -= 1
                if gear_fourth_time <= 0:
                    gear_fourth_active = False
            
            # Update message timer
            if message_timer > 0:
                message_timer -= 1
            
            # Update pirate spawn timer
            if not boss_battle:
                pirate_spawn_timer += 1
                if pirate_spawn_timer >= pirate_spawn_interval:
                    pirates.append(Pirate())
                    pirate_spawn_timer = 0
                    
                    # Make pirates spawn faster as score increases, but respect difficulty
                    if difficulty == "EASY":
                        pirate_spawn_interval = max(60, 120 - score // 20)
                    elif difficulty == "MEDIUM":
                        pirate_spawn_interval = max(45, 90 - score // 15)
                    else:  # HARD":
                        pirate_spawn_interval = max(30, 60 - score // 10)
            
            # Check for boss battle trigger
            if not boss_battle and score > 0 and score % 50 == 0 and len(pirates) == 0:
                boss_battle = True
                if current_island == 0:
                    boss = Arlong(WIDTH // 2, HEIGHT // 4)
                elif current_island == 1:
                    boss = Crocodile(WIDTH // 2, HEIGHT // 4)
                else:
                    boss = Enel(WIDTH // 2, HEIGHT // 4)
                
                message = f"Boss Battle: {boss.name} appears!"
                message_timer = 180  # 3 seconds
            
            # Update boss if in boss battle
            if boss_battle and boss:
                boss.update(luffy.x, luffy.y)
                
                # Boss attacks
                if boss.attack_cooldown <= 0:
                    boss.attack({
                        'luffy': luffy,
                        'boss_attacks': boss_attacks,
                        'pirates': pirates,
                        'Pirate': Pirate
                    })
            
            # Update and draw punches
            for punch in punches[:]:
                punch.update()
                if not punch.active:
                    punches.remove(punch)
                else:
                    punch.draw(screen)
            
            # Update and draw special moves
            for special in special_moves[:]:
                special.update()
                if not special.active:
                    special_moves.remove(special)
                else:
                    special.draw(screen)
            
            # Update and draw special attacks from crew members
            for attack in special_attacks[:]:
                attack.update()
                if not attack.active:
                    special_attacks.remove(attack)
                else:
                    attack.draw(screen)
            
            # Update and draw boss attacks
            for attack in boss_attacks[:]:
                attack.update()
                if not attack.active:
                    boss_attacks.remove(attack)
                else:
                    attack.draw(screen)
            
            # Update and draw power-ups
            for power_up in power_ups[:]:
                power_up.update()
                if power_up.collected:
                    power_ups.remove(power_up)
                else:
                    power_up.draw(screen)
                    
                    # Check if Luffy collects power-up
                    if power_up.check_collision(luffy):
                        result = power_up.apply_effect({
                            'score': score,
                            'pirates': pirates,
                            'gear_fourth_active': gear_fourth_active,
                            'gear_fourth_time': gear_fourth_time,
                            'current_island': current_island,
                            'islands': islands,
                            'boss_battle': boss_battle,
                            'crew_members': crew_members
                        })
                        power_up.collected = True
                        
                        # Update game state based on power-up effect
                        if "Gear Fourth" in result:
                            gear_fourth_active = True
                            gear_fourth_time = 600  # 10 seconds
                        
                        if "Navigating to" in result:
                            current_island = (current_island + 1) % len(islands)
                            boss_battle = True
                        
                        message = result
                        message_timer = 180  # 3 seconds
            
            # Draw Luffy first so he appears behind pirates
            luffy.draw(screen)
            
            # Update and draw pirates, check for collisions
            for pirate in pirates[:]:
                pirate.update()
                
                # Check if pirate collides with Luffy
                if pirate.collides_with_luffy(luffy):
                    if sounds_loaded:
                        game_over_sound.play()
                    game_state = GAME_OVER
                    break
                
                # Check if pirate collides with any punch
                hit = False
                for punch in punches[:]:
                    if punch.active and punch.collides_with_pirate(pirate):
                        pirate.health -= 1
                        if pirate.health <= 0:
                            pirates.remove(pirate)
                            score += 1
                            
                            # Increment combo counter
                            luffy.combo_count += 1
                            luffy.combo_timer = luffy.combo_max_time
                            
                            # Chance to drop power-up
                            if random.random() < 0.1:  # 10% chance
                                power_up_types = [MeatPowerUp, DevilFruitPowerUp, LogPosePowerUp, 
                                                TreasurePowerUp, RumbleBallPowerUp]
                                power_up_class = random.choice(power_up_types)
                                power_ups.append(power_up_class(pirate.x, pirate.y))
                            
                            # Check for crew member unlocks
                            for crew_member in crew_members:
                                if not crew_member.unlocked and hasattr(crew_member, 'unlock_score') and score >= crew_member.unlock_score:
                                    crew_member.unlocked = True
                                    message = f"{crew_member.name} has joined your crew!"
                                    message_timer = 180  # 3 seconds
                        
                        punches.remove(punch)
                        if sounds_loaded:
                            hit_sound.play()
                        hit = True
                        break
                
                # Check if pirate is hit by special attacks
                if not hit:
                    for attack in special_attacks[:]:
                        if attack.active and attack.check_collision(pirate):
                            pirate.health -= attack.damage
                            if pirate.health <= 0:
                                pirates.remove(pirate)
                                score += 1
                            hit = True
                            break
                
                # Check if pirate is in range of Gear Second
                if not hit:
                    for special in special_moves[:]:
                        if special.active and special.collides_with_pirate(pirate):
                            pirate.health -= 0.05  # Continuous damage
                            if pirate.health <= 0:
                                pirates.remove(pirate)
                                score += 1
                                if sounds_loaded:
                                    hit_sound.play()
                                hit = True
                                break
                
                if not hit and pirate in pirates:  # Make sure pirate still exists
                    pirate.draw(screen)
            
            # Draw boss if in boss battle
            if boss_battle and boss:
                # Check if boss is hit by punches
                for punch in punches[:]:
                    if punch.active and punch.collides_with_pirate(boss):
                        boss_defeated = boss.take_damage(1)
                        punches.remove(punch)
                        if sounds_loaded:
                            hit_sound.play()
                        
                        if boss_defeated:
                            boss_battle = False
                            score += 20
                            message = f"{boss.name} has been defeated!"
                            message_timer = 180  # 3 seconds
                
                # Check if boss is hit by special attacks
                for attack in special_attacks[:]:
                    if attack.active and attack.check_collision(boss):
                        boss_defeated = boss.take_damage(attack.damage)
                        if boss_defeated:
                            boss_battle = False
                            score += 20
                            message = f"{boss.name} has been defeated!"
                            message_timer = 180  # 3 seconds
                
                # Draw boss if not defeated
                if not boss.defeated:
                    boss.draw(screen)
            
            # Draw score with shadow
            score_text = font.render(f"Pirates Defeated: {score}", True, WHITE)
            score_shadow = font.render(f"Pirates Defeated: {score}", True, BLACK)
            screen.blit(score_shadow, (12, 12))
            screen.blit(score_text, (10, 10))
            
            # Draw controls help
            controls_text = small_font.render("Left Click: Punch | Right Click: Gear Second | P: Pause", True, WHITE)
            controls_shadow = small_font.render("Left Click: Punch | Right Click: Gear Second | P: Pause", True, BLACK)
            screen.blit(controls_shadow, (WIDTH - controls_text.get_width() - 8, 12))
            screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, 10))
            
            # Draw difficulty indicator
            diff_text = small_font.render(f"Difficulty: {difficulty}", True, WHITE)
            diff_shadow = small_font.render(f"Difficulty: {difficulty}", True, BLACK)
            screen.blit(diff_shadow, (12, 52))
            screen.blit(diff_text, (10, 50))
            
            # Draw island name
            island_text = small_font.render(f"Island: {islands[current_island]}", True, WHITE)
            island_shadow = small_font.render(f"Island: {islands[current_island]}", True, BLACK)
            screen.blit(island_shadow, (12, 92))
            screen.blit(island_text, (10, 90))
            
            # Draw active crew member
            if active_crew_member:
                crew_text = small_font.render(f"Crew: {active_crew_member.name} (E)", True, WHITE)
                crew_shadow = small_font.render(f"Crew: {active_crew_member.name} (E)", True, BLACK)
                screen.blit(crew_shadow, (12, 132))
                screen.blit(crew_text, (10, 130))
                
                # Draw cooldown
                if active_crew_member.current_cooldown > 0:
                    cooldown_percent = active_crew_member.current_cooldown / active_crew_member.ability_cooldown
                    pygame.draw.rect(screen, RED, (10, 160, 100, 10))
                    pygame.draw.rect(screen, GREEN, (10, 160, 100 * (1 - cooldown_percent), 10))
            
            # Draw message if active
            if message and message_timer > 0:
                message_text = font.render(message, True, YELLOW)
                message_shadow = font.render(message, True, BLACK)
                screen.blit(message_shadow, (WIDTH//2 - message_text.get_width()//2 + 2, HEIGHT - 50 + 2))
                screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT - 50))
    
    elif game_state == GAME_OVER:
        restart_button, menu_button = draw_game_over_screen()
    
    elif game_state == CREW_SELECTION:
        crew_buttons, back_button = draw_crew_selection()
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
