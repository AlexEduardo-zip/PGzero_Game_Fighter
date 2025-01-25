import pgzrun
import random
from pygame import Rect
import pygame
import time

WIDTH = 1024
HEIGHT = 768
TITLE = "Shinobi Fighter"

TILE_SIZE = 64  

GRAVITY = 0.5
JUMP_STRENGTH = -10
player_dead = False

level = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0],
    [3, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

tiles = {
    0: None,
    1: pygame.transform.scale(images.ground_11, (64, 64)),
    2: pygame.transform.scale(images.brick_01, (64, 64)),
    3: pygame.transform.scale(images.wooden_box, (64, 64))
}

def draw_level(level):
    for row_idx, row in enumerate(level):
        for col_idx, tile in enumerate(row):
            if tile in tiles and tiles[tile]:
                x = col_idx * (TILE_SIZE)
                y = row_idx * (TILE_SIZE)
                screen.blit(tiles[tile], (x, y))

class Character:
    def __init__(self, pos, animations, health, speed):
        self.pos = list(pos)
        self.vel_x = 0 
        self.vel_y = 0
        self.on_ground = False
        self.direction = "right"
        self.anim_index = 0
        self.current_animation = "idle"
        self.frame_time = 0
        self.health = health
        self.speed = speed
        self.animations = animations
        self.is_attacking = False

    def move(self, direction):
        if direction == "right" and self.pos[0] < WIDTH - (TILE_SIZE):
            self.pos[0] += self.speed
            self.direction = "right"
            self.current_animation = "walk"
        elif direction == "left" and self.pos[0] > 0:
            self.pos[0] -= self.speed
            self.direction = "left"
            self.current_animation = "walk"


    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.pos[1] += self.vel_y
        self.on_ground = False

        char_rect = Rect(self.pos[0] + 55, self.pos[1] + 48, 20, 80)  
        
        for row_idx, row in enumerate(level):
            for col_idx, tile in enumerate(row):
                if tile != 0:  
                    tile_rect = Rect(col_idx * 64, row_idx * 64, 64, 64) 
                    
                    if char_rect.colliderect(tile_rect):
                        if self.vel_y > 0:  
                            self.pos[1] = tile_rect.top - 128  
                            self.vel_y = 0
                            self.on_ground = True
                        
                        elif self.vel_y < 0:  
                            self.pos[1] = tile_rect.bottom
                            self.vel_y = 0
                        
                        if self.vel_x > 0: 
                            if char_rect.colliderect(tile_rect):
                                self.pos[0] = tile_rect.left - 44  
                                self.vel_x = 0
                        elif self.vel_x < 0:  
                            if char_rect.colliderect(tile_rect):
                                self.pos[0] = tile_rect.right - 44  
                                self.vel_x = 0

                        if self.vel_y > 0:  
                            if self.pos[1] + 80 > tile_rect.top and self.pos[1] < tile_rect.bottom:
                                self.pos[1] = tile_rect.top - 80
                                self.vel_y = 0
                                self.on_ground = True

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_animation = "attack"
            self.anim_index = 0

    def update_animation(self):
        self.frame_time += 1
        if self.frame_time >= 12:  
            self.frame_time = 0
            self.anim_index += 1
            total_frames = len(self.animations[self.current_animation]["frames"])

            if self.anim_index >= total_frames:
                if self.current_animation == "attack":
                    self.current_animation = "idle"
                    self.is_attacking = False
                    self.anim_index = 0
                elif self.current_animation == "walk" and not (keys_held["left"] or keys_held["right"]):
                    self.current_animation = "idle"
                    self.anim_index = 0
                elif self.current_animation == "dead":
                    self.anim_index = total_frames - 1
                else:
                    self.anim_index = 0

    def draw(self):
        anim_data = self.animations[self.current_animation]
        spritesheet = anim_data["spritesheet"]
        frame = anim_data["frames"][self.anim_index]
        x, y = frame * anim_data["sprite_size"][0], 0
        sprite_width, sprite_height = anim_data["sprite_size"]

        if self.direction == "right":
            screen.surface.blit(spritesheet, self.pos, (x, y, sprite_width, sprite_height))
        else:
            flipped = pygame.transform.flip(
                spritesheet.subsurface(Rect(x, y, sprite_width, sprite_height)), True, False
            )
            screen.surface.blit(flipped, (self.pos[0], self.pos[1]))

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

class Hero(Character):
    def __init__(self, pos, animations):
        super().__init__(pos, animations, health=3, speed=5)

    def attack(self, enemies):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_animation = "attack"
            self.anim_index = 0
            self.update_animation()
            for enemy in enemies:
                enemy_rect = Rect(enemy.pos[0] + 20, enemy.pos[1] + 48, 50, 80)
                hero_rect = Rect(self.pos[0] + 20, self.pos[1] + 48, 50, 80)
                if hero_rect.colliderect(enemy_rect):
                    enemy.health = 0
                    enemy.respawn() 
                    print("Inimigo derrotado!")

class Enemy(Character):
    def __init__(self, pos, animations):
        super().__init__(pos, animations, health=2, speed=1)
        self.attack_cooldown = 3  
        self.last_attack_time = time.time() 

    def update(self, hero):
        if self.is_attacking:
            self.update_animation()
            return

        if self.current_animation != "dead":
            
            if self.pos[0] < hero.pos[0]:
                self.move("right")
            elif self.pos[0] > hero.pos[0]:
                self.move("left")

            enemy_rect = Rect(self.pos[0] + 40, self.pos[1] + 48, 20, 80)
            hero_rect = Rect(hero.pos[0] + 40, hero.pos[1], 20, TILE_SIZE)

            if enemy_rect.colliderect(hero_rect) and time.time() - self.last_attack_time > self.attack_cooldown:
                self.attack()  
                self.is_attacking = True
                self.current_animation = "attack"
                self.anim_index = 0
                self.last_attack_time = time.time() 
                hero.health -= 1
                update_hero_health()
                self.update_animation()
                print("Inimigo atacou!")

            self.update_animation()  
        else:
            self.respawn()
        self.apply_gravity()

    def respawn(self):
        if self.current_animation != "dead":
            self.current_animation = "dead"
            self.anim_index = 0
            self.frame_time = 0
            print("Inimigo morreu!")
        else:
            total_frames = len(self.animations["dead"]["frames"])
            if self.anim_index >= total_frames - 1:  
                time.sleep(0.5)  
                self.health = 2
                increment_enemies_defeated() 
                self.pos = [random.randint(100, WIDTH - 100), HEIGHT - 228]  
                self.current_animation = "idle"  
                print("Inimigo respawnado!")

hero = Hero(
    (TILE_SIZE // 2, HEIGHT - TILE_SIZE * 2),
    animations={
        "idle": {"spritesheet": images.hero_idle, "sprite_size": (128, 128), "frames": [0, 1, 2, 3, 4, 5]},
        "walk": {"spritesheet": images.hero_run, "sprite_size": (128, 128), "frames": [0, 1, 2, 3, 4, 5, 6, 7]},
        "attack": {"spritesheet": images.hero_attack_1, "sprite_size": (128, 128), "frames": [0, 1, 2, 3, 4, 5]},
        "dead": {"spritesheet": images.hero_dead, "sprite_size": (128, 128), "frames": [0, 1, 2]},
    },
)

enemy = Enemy(
    (TILE_SIZE * 4, HEIGHT - TILE_SIZE * 2),
    animations={
        "idle": {"spritesheet": images.enemy_idle, "sprite_size": (128, 128), "frames": [0, 1, 2, 3, 4, 5]},
        "walk": {"spritesheet": images.enemy_run, "sprite_size": (128, 128), "frames": [0, 1, 2, 3, 4, 5, 6, 7]},
        "attack": {"spritesheet": images.enemy_attack_3, "sprite_size": (128, 128), "frames": [0, 1, 2, 3]},
        "dead": {"spritesheet": images.enemy_dead, "sprite_size": (128, 128), "frames": [0, 1, 2]},
    },
)

menu_active = True
keys_held = {"left": False, "right": False}
background_image = images.background_01
music_on = True
hero_health = 3  
enemies_defeated = 0   
music.play("background_music")
music.set_volume(0.5)

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

buttons = [
    {"text": "Começar Jogo", "action": "start_game"},
    {"text": "Música: Ligada", "action": "toggle_music"},
    {"text": "Saída", "action": "exit_game"},
]

button_width = 200
button_height = 50
button_spacing = 20
button_positions = [
    (WIDTH // 2 - button_width // 2, HEIGHT // 2 - (button_height + button_spacing) * len(buttons) // 2 + i * (button_height + button_spacing))
    for i in range(len(buttons))
]

def increment_enemies_defeated():
    global enemies_defeated
    enemies_defeated += 1
    print(f"Inimigos derrotados: {enemies_defeated}")

def update_hero_health():
    global hero_health, menu_active

    if hero.health >= 0:
        hero_health -= 1 

        if hero_health <= 0:
            menu_active = True  
            hero.health = 3 
        else:
            print(f"Você perdeu uma vida. Vidas restantes: {hero_health}")


def draw():
    if menu_active:
        screen.clear()
        screen.blit(background_image, (0, 0))

        screen.draw.text("Shinobi Fighter", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")

        for i, button in enumerate(buttons):
            x, y = button_positions[i]
            screen.draw.filled_rect(Rect((x, y), (button_width, button_height)), WHITE)
            screen.draw.text(
                button["text"],
                center=(x + button_width // 2, y + button_height // 2),
                fontsize=30,
                color=BLACK,
            )
    else:
        screen.blit(background_image, (0, 0))
        draw_level(level)

        screen.draw.text(f"Vida: {hero_health}", topleft=(10, 10), fontsize=30, color="white")
        screen.draw.text(f"Inimigos derrotados: {enemies_defeated}", topleft=(10, 50), fontsize=30, color="white")

        hero.update_animation()
        hero.draw()
        enemy.update(hero)
        enemy.update_animation()
        enemy.draw()

def on_mouse_down(pos):
    global menu_active, music_on
    if menu_active:
        for i, button in enumerate(buttons):
            x, y = button_positions[i]
            if Rect((x, y), (button_width, button_height)).collidepoint(pos):
                handle_button_action(button["action"])
                break

def handle_button_action(action):
    global menu_active, music_on

    if action == "start_game":
        menu_active = False
    elif action == "toggle_music":
        music_on = not music_on
        if music_on:
            music.play("background_music")
            buttons[1]["text"] = "Música: Ligada"
        else:
            music.stop()
            buttons[1]["text"] = "Música: Desligada"
    elif action == "exit_game":
        exit()  

def update():
    global hero_health, enemies_defeated

    if menu_active:
        return

    if hero.is_attacking:
        hero.update_animation()
        return

    if keys_held["left"]:
        hero.move("left")
    elif keys_held["right"]:
        hero.move("right")

    hero.apply_gravity()
    hero.update_animation()

    enemy.update(hero) 

def on_key_down(key):
    global menu_active  
    if key == pygame.K_LEFT:
        keys_held["left"] = True
    elif key == pygame.K_RIGHT:
        keys_held["right"] = True
    elif key == pygame.K_RETURN:
        menu_active = False
    elif key == pygame.K_SPACE:
        if not hero.is_attacking:  
            hero.attack([enemy])

def on_key_up(key):
    if key == pygame.K_LEFT:
        keys_held["left"] = False
    elif key == pygame.K_RIGHT:
        keys_held["right"] = False

pgzrun.go()
