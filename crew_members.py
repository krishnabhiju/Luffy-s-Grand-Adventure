# Define crew members
class CrewMember:
    def __init__(self, name, image=None, ability_name="", ability_cooldown=600):
        self.name = name
        self.image = image  # Will be None for now, would be a loaded image in full implementation
        self.ability_name = ability_name
        self.ability_cooldown = ability_cooldown
        self.current_cooldown = 0
        self.unlocked = False
        self.level = 1
    
    def use_ability(self, game_state_data):
        if self.current_cooldown <= 0:
            self.current_cooldown = self.ability_cooldown
            return self.ability_effect(game_state_data)
        return False
    
    def ability_effect(self, game_state_data):
        # Override in subclasses
        pass
    
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

# Define specific crew members
class Zoro(CrewMember):
    def __init__(self):
        super().__init__("Zoro", None, "Three Sword Style", 900)
        self.unlock_score = 10
    
    def ability_effect(self, game_state_data):
        # Create slashing attacks in three directions
        angles = [0, 2*math.pi/3, 4*math.pi/3]
        for angle in angles:
            dx = math.cos(angle) * 400
            dy = math.sin(angle) * 400
            end_x = game_state_data['luffy'].x + dx
            end_y = game_state_data['luffy'].y + dy
            game_state_data['special_attacks'].append(
                SwordSlash(game_state_data['luffy'].x, game_state_data['luffy'].y, end_x, end_y)
            )
        return True

class Nami(CrewMember):
    def __init__(self):
        super().__init__("Nami", None, "Thunderbolt Tempo", 800)
        self.unlock_score = 20
    
    def ability_effect(self, game_state_data):
        # Create lightning strikes on all pirates
        for pirate in game_state_data['pirates'][:]:
            game_state_data['special_attacks'].append(
                ThunderAttack(pirate.x, pirate.y)
            )
        return True

class Usopp(CrewMember):
    def __init__(self):
        super().__init__("Usopp", None, "Fire Star", 600)
        self.unlock_score = 30
    
    def ability_effect(self, game_state_data):
        # Shoot 5 projectiles in a spread pattern
        for i in range(5):
            angle = math.pi/2 - math.pi/6 * (i - 2)
            dx = math.cos(angle) * 400
            dy = -math.sin(angle) * 400  # Negative because y increases downward
            end_x = game_state_data['luffy'].x + dx
            end_y = game_state_data['luffy'].y + dy
            game_state_data['special_attacks'].append(
                FireStar(game_state_data['luffy'].x, game_state_data['luffy'].y, end_x, end_y)
            )
        return True

class Sanji(CrewMember):
    def __init__(self):
        super().__init__("Sanji", None, "Diable Jambe", 750)
        self.unlock_score = 40
    
    def ability_effect(self, game_state_data):
        # Create a spinning kick attack that hits all nearby pirates
        game_state_data['special_attacks'].append(
            DiableJambe(game_state_data['luffy'].x, game_state_data['luffy'].y)
        )
        return True

class Chopper(CrewMember):
    def __init__(self):
        super().__init__("Chopper", None, "Rumble Ball", 1000)
        self.unlock_score = 50
    
    def ability_effect(self, game_state_data):
        # Heal Luffy (would be implemented if health system was added)
        # For now, clear all pirates on screen
        for pirate in game_state_data['pirates'][:]:
            game_state_data['pirates'].remove(pirate)
            game_state_data['score'] += 1
        return True

class Robin(CrewMember):
    def __init__(self):
        super().__init__("Robin", None, "Clutch", 700)
        self.unlock_score = 60
    
    def ability_effect(self, game_state_data):
        # Immobilize all pirates for a short time
        for pirate in game_state_data['pirates']:
            pirate.immobilized = True
            pirate.immobilize_time = 180  # 3 seconds
        return True

class Franky(CrewMember):
    def __init__(self):
        super().__init__("Franky", None, "Radical Beam", 850)
        self.unlock_score = 70
    
    def ability_effect(self, game_state_data):
        # Fire a powerful beam across the screen
        mouse_pos = pygame.mouse.get_pos()
        game_state_data['special_attacks'].append(
            RadicalBeam(game_state_data['luffy'].x, game_state_data['luffy'].y, 
                       mouse_pos[0], mouse_pos[1])
        )
        return True

class Brook(CrewMember):
    def __init__(self):
        super().__init__("Brook", None, "Soul Solid", 800)
        self.unlock_score = 80
    
    def ability_effect(self, game_state_data):
        # Freeze all pirates
        for pirate in game_state_data['pirates']:
            pirate.frozen = True
            pirate.freeze_time = 120  # 2 seconds
        return True

class Jinbe(CrewMember):
    def __init__(self):
        super().__init__("Jinbe", None, "Fish-Man Karate", 900)
        self.unlock_score = 90
    
    def ability_effect(self, game_state_data):
        # Create a water wave that pushes all pirates back
        game_state_data['special_attacks'].append(
            WaterWave(game_state_data['luffy'].x, game_state_data['luffy'].y)
        )
        return True
