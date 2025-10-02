import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()

victory = False


spell2shoot=False
spell2_available = False
lastspellshoot=False
lastspell_availabe=False


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mage Platformer')

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 25
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# Player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

newability = False
newability_thrown = False

# Load sounds
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)

# Load images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

# Background
bg_img = pygame.image.load('img/Background/image.png').convert_alpha()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Tiles
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


# Add this with the other bullet image loads
spell2_bullet_img = pygame.image.load('img/icons/NEW.png').convert_alpha()
spell2_bullet_img = pygame.transform.scale(spell2_bullet_img, (60, 50))

lastspell_bullet_img = pygame.image.load('img/icons/water40005.png').convert_alpha()
lastspell_bullet_img = pygame.transform.scale(lastspell_bullet_img, (40, 30))
# Bullets
# Bullets
bullet_img = pygame.image.load('img/icons/fire.png').convert_alpha()
fire_bullet_img = pygame.image.load('img/icons/fire.png').convert_alpha()
earth_bullet_img = pygame.image.load('img/icons/earth.png').convert_alpha()
# After loading the water bullet image:
water_bullet_img = pygame.image.load('img/icons/water_bullet.png').convert_alpha()
water_bullet_img = pygame.transform.scale(water_bullet_img, (15, 8))
boss_bullet_img = pygame.image.load('img/icons/boss_bullet.png').convert_alpha()
boss_bullet_img=pygame.transform.scale(boss_bullet_img,(15,8))

twoenemy_bullet_img = pygame.image.load('img/icons/2enemy2_bullet.png').convert_alpha()
twoenemy_bullet_img = pygame.transform.scale(twoenemy_bullet_img, (70, 80))
# Grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

# Item boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    screen.blit(bg_img, (0, 0))


def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # AI variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load animations
        if char_type == 'Waterenemy':
            animation_types = ['Idle', 'Run', 'Attack', 'Death']
        elif char_type == '3enemyflast':
            animation_types = ['Idle', 'Run', 'Attack', 'Death']
        else:
            animation_types = ['Idle', 'Run', 'Jump', 'Death']

        for animation in animation_types:
            temp_list = []
            if char_type == '2enemy2':
                num_of_frames = 6
            elif char_type == 'Waterenemy' and animation == 'Death':
                num_of_frames = 6
            else:
                num_of_frames = len(os.listdir(f'img/{char_type}/{animation}'))

            for i in range(num_of_frames):
                try:
                    img = pygame.image.load(f'img/{char_type}/{animation}/{i}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                except:
                    print(f"Missing frame: img/{char_type}/{animation}/{i}.png")
                    break
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Boss-specific initialization (AFTER rect is created)
        if char_type == '3enemyflast':
            self.health = 500
            self.max_health = self.health
            self.special_attack_cooldown = 0
            self.vision = pygame.Rect(0, 0, 700, 500)
            self.shoot_offset_y = 0.4 * self.rect.height  # Now rect exists
            self.attack_pattern = 0
            self.attack_cooldown = 0


        if char_type == 'Waterenemy':
            self.contact_damage = False  # No damage on contact
            self.attack_cooldown = 0

        # Load animations
        if char_type == 'Waterenemy':
            animation_types = ['Idle', 'Run', 'Attack', 'Death']
        elif char_type == '3enemyflast':
            animation_types = ['Idle', 'Run', 'Attack', 'Death'] # Simple animations only
        else:
            animation_types = ['Idle', 'Run', 'Jump', 'Death']



        if char_type == 'Waterenemy':
            self.health = 100  # Same as other enemies
            self.max_health = self.health

        for animation in animation_types:
            temp_list = []
            # Handle frame counts for specific enemies
            if char_type == '2enemy2':
                num_of_frames = 6  # You have 0-5.png (6 frames)
            elif char_type == 'Waterenemy' and animation == 'Death':
                num_of_frames = 6
            else:
                # Default: count files in directory
                num_of_frames = len(os.listdir(f'img/{char_type}/{animation}'))

            for i in range(num_of_frames):
                try:
                    img = pygame.image.load(f'img/{char_type}/{animation}/{i}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                except:
                    print(f"Missing frame: img/{char_type}/{animation}/{i}.png")
                    break
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump (disabled for Waterenemy)
        if self.char_type != 'Waterenemy' and self.jump and not self.in_air:
            self.vel_y = -14
            self.jump = False
            self.in_air = True
            jump_fx.play()

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Collision detection
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == 'fire':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'fire':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0:
            # Use world position for bullet spawn
            spawn_x = self.rect.centerx + (0.6 * self.rect.size[0] * self.direction) + bg_scroll
            spawn_y = self.rect.centery

            bullet = Bullet(spawn_x, spawn_y, self.direction, self.char_type)
            bullet_group.add(bullet)
            self.shoot_cooldown = 45
            shot_fx.play()

            if self.char_type == '3enemyflast':
                spawn_x = self.rect.centerx + (0.6 * self.rect.size[0] * self.direction)
                spawn_y = self.rect.centery + (0.4 * self.rect.height)  # Lower position
            else:
                spawn_x = self.rect.centerx + (0.6 * self.rect.size[0] * self.direction)
                spawn_y = self.rect.centery

                # Create bullet in world space (add bg_scroll to x position)
            bullet = Bullet(spawn_x + bg_scroll, spawn_y, self.direction, self.char_type)
            bullet_group.add(bullet)

            # Set different cooldown for boss
            if self.char_type == '3enemyflast':
                self.shoot_cooldown = 30  # Faster cooldown for testing
            else:
                self.shoot_cooldown = 45

            shot_fx.play()

            if self.char_type == 'Waterenemy':
                # Create properly sized water bullet
                bullet = Bullet(self.rect.centerx, self.rect.centery,
                                self.direction, self.char_type)
                bullet_group.add(bullet)
                shot_fx.play()
            else:
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                                self.rect.centery, self.direction, self.char_type)
                bullet_group.add(bullet)
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            vision_offset = 100
            self.vision.center = (
                self.rect.centerx + vision_offset * self.direction,
                self.rect.centery
            )


            if self.char_type == '3enemyflast':
                if self.char_type == '3enemyflast':
                    # Boss-specific AI
                    self.vision.center = (
                        self.rect.centerx + 300 * self.direction,
                        self.rect.centery
                    )

                    # Always face player
                    if player.rect.centerx > self.rect.centerx:
                        self.direction = 1
                        self.flip = False
                    else:
                        self.direction = -1
                        self.flip = True

                    # Attack when player is in vision
                    if self.vision.colliderect(player.rect):
                        self.update_action(2)  # Attack animation

                        # Shoot with pattern
                        if self.attack_cooldown <= 0:
                            if self.attack_pattern == 0:
                                # Triple shot
                                for i in range(3):
                                    self.shoot()
                                    pygame.time.delay(100)  # Small delay between shots
                                self.attack_pattern = 1
                            else:
                                # Powerful single shot
                                self.shoot()
                                self.attack_pattern = 0
                            self.attack_cooldown = 120  # Cooldown between attack patterns

                        self.attack_cooldown -= 1

                    # Movement - boss stays mostly stationary
                    if random.randint(1, 200) == 1:
                        if self.direction == 1:
                            self.move(False, True)
                        else:
                            self.move(True, False)



            elif self.char_type == 'Waterenemy':
                # Shooting logic
                if random.randint(1, 60) == 1:  # Adjust frequency as needed
                    self.update_action(2)  # Attack animation
                    self.shoot()

                # Simple movement pattern
                if self.direction == 1:
                    self.move(False, True)
                else:
                    self.move(True, False)

                self.move_counter += 1
                if self.move_counter > TILE_SIZE * 3:
                    self.direction *= -1
                    self.move_counter = 0
            else:
                # Default AI for other enemies
                if self.idling == False and random.randint(1, 200) == 1:
                    self.update_action(0)
                    self.idling = True
                    self.idling_counter = 50

                if self.vision.colliderect(player.rect):
                    self.update_action(0)
                    self.shoot()
                else:
                    if self.idling == False:
                        if self.direction == 1:
                            ai_moving_right = True
                        else:
                            ai_moving_right = False
                        ai_moving_left = not ai_moving_right
                        self.move(ai_moving_left, ai_moving_right)
                        self.update_action(1)
                        self.move_counter += 1
                        self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                        if self.move_counter > TILE_SIZE:
                            self.direction *= -1
                            self.move_counter *= -1
                    else:
                        self.idling_counter -= 1
                        if self.idling_counter <= 0:
                            self.idling = False

        self.rect.x += screen_scroll

    def shoot_spell2(self):
        if self.shoot_cooldown == 0:
            spawn_x = self.rect.centerx + (0.6 * self.rect.size[0] * self.direction) + bg_scroll
            spawn_y = self.rect.centery
            bullet = Bullet(spawn_x, spawn_y, self.direction, 'spell2')  # Use 'spell2' as char_type
            bullet_group.add(bullet)
            self.shoot_cooldown = 5

            shot_fx.play()

    def lastspellshoot(self):
        if self.shoot_cooldown==0:
            spawn_x = self.rect.centerx + (0.6 * self.rect.size[0] * self.direction) + bg_scroll
            spawn_y = self.rect.centery

            bullet = Bullet(spawn_x, spawn_y, self.direction, 'lastspell')  # Use 'spell2' as char_type
            bullet_group.add(bullet)
            self.shoot_cooldown = 45

            shot_fx.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]

        # Check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Handle animation looping or ending
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:  # Death animation
                self.frame_index = len(self.animation_list[self.action]) - 1  # Stay on last frame
            else:
                self.frame_index = 0  # Loop other animations

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)  # Switch to death animation

            # For Waterenemy specifically - make sure it stays in death animation
            if self.char_type == 'Waterenemy':
                self.frame_index = 0  # Start death animation from beginning
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Soldier('fire', x * TILE_SIZE, y * TILE_SIZE, 0.9, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # create enemies
                        enemy = Soldier('Golem', x * TILE_SIZE, y * TILE_SIZE, 0.15, 2, 20, 0)
                        enemy_group.add(enemy)
                    # elif tile == 17: # create ammo box
                    #     item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                    #     item_box_group.add(item_box)
                    # elif tile == 18: # create grenade box
                    #     item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                    #     item_box_group.add(item_box)
                    elif tile == 19:  # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 21:
                        enemy = Soldier('mini1', x * TILE_SIZE, y * TILE_SIZE, 1.2, 2, 20, 0)
                        enemy_group.add(enemy)
                        # health_bar = HealthBar(x * TILE_SIZE, (y * TILE_SIZE) - 10, enemy.health, enemy.max_health)  # Position health bar above the enemy
                        # enemy.health_bar = health_bar  # Correct indentation here


                    elif tile == 22:  # create Waterenemy
                        enemy = Soldier('Waterenemy', x * TILE_SIZE, y * TILE_SIZE, 1.0, 2, 20, 0)
                        enemy_group.add(enemy)


                    elif tile == 23:  # create 2enemy2 (use an unused tile number, like 23)

                        enemy = Soldier('2enemy2', x * TILE_SIZE, y * TILE_SIZE, 1.5, 3, 20, 0)

                        enemy.health = 300  # Triple the default health (100 → 300)
                        enemy.max_health = enemy.health

                        enemy_group.add(enemy)

                    elif tile == 24:  # New tile number for final boss
                        boss = Soldier('3enemyflast', x * TILE_SIZE, y * TILE_SIZE, 3.0, 2, 50, 10)
                        enemy_group.add(boss)
                        boss.health = 500  # Triple health
                        boss.max_health = boss.health
                        enemy_group.add(boss)


                    elif tile == 20:  # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)


        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, char_type):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.direction = direction
        self.char_type = char_type
        self.world_x = x  # Store world position
        self.world_y = y

        # Set image based on shooter
        if char_type == 'fire':
            self.image = fire_bullet_img
            self.damage = 25

        elif char_type== 'lastspell':
            self.image=lastspell_bullet_img
            self.damage=150

        elif char_type == 'spell2':  # New condition for spell2
            self.image = spell2_bullet_img
            self.damage = 100

        elif char_type == 'Waterenemy':
            self.image = water_bullet_img
            self.damage = 10
        elif char_type == '2enemy2':
            self.image = twoenemy_bullet_img
            self.damage = 15
            self.speed = 5
        elif char_type == '3enemyflast':
            self.image = boss_bullet_img
            self.damage = 30
            self.speed = 5
        else:
            self.image = earth_bullet_img
            self.damage = 5

        self.rect = self.image.get_rect()
        self.rect.center = (x - bg_scroll, y)  # Convert to screen space

    def update(self):
        # Update world position
        self.world_x += (self.direction * self.speed)

        # Convert to screen space
        screen_x = self.world_x - bg_scroll
        self.rect.centerx = screen_x

        # Only kill if way off-screen (more generous bounds)
        if (screen_x < -200) or (screen_x > SCREEN_WIDTH + 200):
            self.kill()
            return

        # Player collision (enemy bullets only)
        if self.char_type != 'fire' and self.char_type!= 'lastspell' and self.char_type!= 'spell2' and pygame.sprite.collide_rect(self, player):
            if player.alive:
                player.health -= self.damage
                self.kill()

        # Enemy collision (player bullets only)
        if self.char_type == 'fire' or self.char_type == 'spell2' or self.char_type== 'lastspell':
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy) and enemy.alive:
                    enemy.health -= self.damage
                    self.kill()
                    break

        # Boundary and obstacle checks
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                break

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom


        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0


    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:#vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.fill(BG)
        #add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        #update background
        draw_bg()
        #draw world map
        world.draw()
        #show player health
        health_bar.draw(player.health)



        player.update()
        player.draw()

        for enemy in enemy_group:
            if pygame.sprite.collide_rect(player, enemy) and enemy.alive:
                # Only deal damage if enemy has contact_damage enabled
                if hasattr(enemy, 'contact_damage') and enemy.contact_damage:
                    player.health -= 10
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        bullet_group.update()



        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0


        #update player actions
        if player.alive:
            if shoot:
                player.shoot()
                player.shoot_cooldown=3
            #throw grenades
            elif spell2shoot and spell2_available:
                player.shoot_spell2()
                spell2shoot=False

            elif lastspellshoot and lastspell_availabe:
                player.lastspellshoot()
                lastspellshoot=False


            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #check if player has completed the level
            if level_complete:
                if level == 3:  # Player completed the final level
                    victory = True
                else:
                    start_intro = True
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level == 2:
                        spell2_available = True
                    if level == 3:
                        lastspell_availabe = True

                    if level <= MAX_LEVELS:
                        # load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)



    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_a:
                shoot = True
            if event.key == pygame.K_z and spell2_available:
                spell2shoot=True
            if event.key == pygame.K_e and lastspell_availabe:
                lastspellshoot=True

            if event.key == pygame.K_UP and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False


        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_UP:
                spell2shoot=False
            if event.key == pygame.K_a:
                shoot = False

    # Show victory message if game is won
    if victory:
        # Create a semi-transparent overlay
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill(BLACK)
        screen.blit(s, (0, 0))

        # Draw victory text
        victory_font = pygame.font.SysFont('Futura', 72)
        victory_text = victory_font.render('VICTORY!', True, WHITE)
        instructions_font = pygame.font.SysFont('Futura', 36)
        instructions_text = instructions_font.render('Press ESCAPE to exit', True, WHITE)

        screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(instructions_text,
                    (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        # Check for ESCAPE key to quit
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False
    pygame.display.update()

pygame.quit()
