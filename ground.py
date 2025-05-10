from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import random
import math
import time


# game er constant gula
window_width = 800
window_height = 600
arena_size = 100
max_player_health = 100
shield_duration = 5.0  # second e
bullet_speed = 1.5
drone_bullet_speed = 1.2  # regular bullet er cheye ektu slow
player_speed = 0.5
drone_speed = 0.2
tank_speed = 0.1
small_drone_health = 1
big_drone_health = 3
max_entities = 10
spawn_interval = 5.0  # second e


# game er state
player_pos = [0, 1, 0]  # x, y, z
player_rot = [0, 0]  # pitch, yaw
player_health = max_player_health
player_shield_active = False
player_shield_end_time = 0
first_person_view = True
last_shot_time = 0
shot_cooldown = 0.5  # second e
paused = False
game_end_time = None  # shuru te none set kora
pause_time = None   # game pause hole time store kore


# mouse er state
mouse_x, mouse_y = 0, 0
last_mouse_x, last_mouse_y = 0, 0
mouse_sensitivity = 0.2


# key state gula
keys = {'w': False, 'a': False, 's': False, 'd': False, 'space': False}


# tank ar megatron kill er counter
tanks_killed = 0
megatron_killed = 0


# ei global gula add kora game state variable er kache
last_spawn_time_tank_red = time.time()  # tank ar red drone spawn korbe 5 second por por
last_spawn_time_blue = time.time()      # blue drone spawn korbe 10 second por por
last_spawn_time_medbox = time.time()    # medbox spawn korbe 10 second por por
last_spawn_time_shield = time.time()    # shield spawn korbe 10 second por por


# game er entity gula
class Entity:
   def __init__(self, x, y, z, type_id):
       self.position = [x, y, z]
       self.type = type_id  # 0: red drone, 1: blue drone, 2: tank, 3: shield, 4: medbox
       self.health = small_drone_health if type_id == 0 else big_drone_health if type_id == 1 else 5
       self.speed = drone_speed if type_id in [0, 1] else tank_speed if type_id == 2 else 0
       self.direction = [random.uniform(-1, 1), random.uniform(-0.5, 0.5), random.uniform(-1, 1)]
       # tank er jonno shooting timer set kora; drone er jonno niche set kora hobe
       self.next_shot_time = time.time() + random.uniform(3, 7) if type_id == 2 else 0
       self.created_time = time.time()
       # direction normalize kora
       mag = math.sqrt(sum(d * d for d in self.direction))
       if mag > 0:
           self.direction = [d / mag for d in self.direction]


class Bullet:
   def __init__(self, x, y, z, dx, dy, dz, player_bullet=True, damage=1, color=None):
       self.position = [x, y, z]
       self.direction = [dx, dy, dz]
       self.player_bullet = player_bullet
       self.alive = True
       self.damage = damage
       # default enemy bullet color white jodi specify na thake
       self.color = color if color is not None else (1.0, 1.0, 1.0)


entities = []
bullets = []
score = 0
gun_level = 1
game_start_time = time.time()
last_spawn_time = time.time()


def init():
   glClearColor(0.0, 0.0, 0.0, 1.0)  # sky er jonno black color
   glEnable(GL_DEPTH_TEST)
   glEnable(GL_LIGHTING)
   glEnable(GL_LIGHT0)
   glEnable(GL_COLOR_MATERIAL)
   glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


   # light er position
   glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
   glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])


   # entity gula initialize kora
   spawn_entity()
   spawn_entity()


def spawn_entity():
   if len(entities) >= max_entities:
       return  # max entity hole spawn bondho
   # tank spawn er probability barano
   entity_type = random.choices(
       [0, 1, 2, 3, 4],  # entity type gula
       weights=[3, 3, 4, 1, 1]  # tank (type 2) er weight beshi
   )[0]


   if entity_type <= 1:  # flying drone
       x = random.uniform(-arena_size / 2, arena_size / 2)
       y = random.uniform(5, 15)
       z = random.uniform(-arena_size / 2, arena_size / 2)
   elif entity_type == 2:  # tank
       x = random.uniform(-arena_size / 2, arena_size / 2)
       y = 0.5  # tank ground er ektu upore thake
       z = random.uniform(-arena_size / 2, arena_size / 2)
   elif entity_type == 3:  # shield
       x = random.uniform(-arena_size / 2, arena_size / 2)
       y = 0
       z = random.uniform(-arena_size / 2, arena_size / 2)
   elif entity_type == 4:  # medbox
       x = random.uniform(-arena_size / 2, arena_size / 2)
       y = 0
       z = random.uniform(-arena_size / 2, arena_size / 2)


   entities.append(Entity(x, y, z, entity_type))


def spawn_tank():
   if len(entities) >= max_entities:
       return
   x = random.uniform(-arena_size / 2, arena_size / 2)
   y = 0.5  # tank ground er ektu upore
   z = random.uniform(-arena_size / 2, arena_size / 2)
   entities.append(Entity(x, y, z, 2))


def spawn_red_drone():
   if len(entities) >= max_entities:
       return
   x = random.uniform(-arena_size / 2, arena_size / 2)
   y = random.uniform(5, 15)
   z = random.uniform(-arena_size / 2, arena_size / 2)
   entities.append(Entity(x, y, z, 0))


def spawn_blue_drone():
   if len(entities) >= max_entities:
       return
   x = random.uniform(-arena_size / 2, arena_size / 2)
   y = random.uniform(5, 15)
   z = random.uniform(-arena_size / 2, arena_size / 2)
   entities.append(Entity(x, y, z, 1))


def spawn_shield():
   if len(entities) >= max_entities:
       return
   x = random.uniform(-arena_size / 2, arena_size / 2)
   y = 0     # shield ground e thake
   z = random.uniform(-arena_size / 2, arena_size / 2)
   entities.append(Entity(x, y, z, 3))


def spawn_medbox():
   if len(entities) >= max_entities:
       return
   x = random.uniform(-arena_size / 2, arena_size / 2)
   y = 0     # medbox ground e
   z = random.uniform(-arena_size / 2, arena_size / 2)
   entities.append(Entity(x, y, z, 4))


def update_entities():
   global player_health, player_shield_active, player_shield_end_time, score, tanks_killed, megatron_killed


   # shield expire check kora
   if player_shield_active and time.time() > player_shield_end_time:
       player_shield_active = False


   # entity gula update kora
   for entity in entities[:]:
       if entity.type <= 1:  # drone (red: type 0; blue: type 1)
           # direction onujayi position update
           entity.position[0] += entity.direction[0] * entity.speed
           entity.position[1] += entity.direction[1] * entity.speed
           entity.position[2] += entity.direction[2] * entity.speed


           # arena boundary te bounce kora
           if abs(entity.position[0]) > arena_size / 2:
               entity.direction[0] *= -1
           if entity.position[1] < 5 or entity.position[1] > 15:
               entity.direction[1] *= -1
           if abs(entity.position[2]) > arena_size / 2:
               entity.direction[2] *= -1


           # drone shooting logic
           if time.time() > entity.next_shot_time:
               if entity.type == 0:
                   # red drone light green bullet fire kore, kom damage, beshi frequent
                   rand_dx = random.uniform(-1, 1)
                   rand_dy = random.uniform(-1, 1)
                   rand_dz = random.uniform(-1, 1)
                   mag = math.sqrt(rand_dx**2 + rand_dy**2 + rand_dz**2)
                   if mag > 0:
                       rand_dx /= mag; rand_dy /= mag; rand_dz /= mag
                   bullet = Bullet(
                       entity.position[0], entity.position[1], entity.position[2],
                       rand_dx, rand_dy, rand_dz,
                       player_bullet=False, damage=1, color=(0.7, 1.0, 0.7)  # light green
                   )
                   entity.next_shot_time = time.time() + random.uniform(1, 2)
               elif entity.type == 1:
                   # blue drone (megatron) player er dike aim kore
                   dx = player_pos[0] - entity.position[0]
                   dy = player_pos[1] - entity.position[1]
                   dz = player_pos[2] - entity.position[2]
                   mag = math.sqrt(dx*dx + dy*dy + dz*dz)
                   if mag > 0:
                       dx, dy, dz = dx/mag, dy/mag, dz/mag
                   bullet = Bullet(
                       entity.position[0], entity.position[1], entity.position[2],
                       dx, dy, dz,
                       player_bullet=False, damage=3, color=(1.0, 0.8, 0.5)  # light orange
                   )
                   entity.next_shot_time = time.time() + random.uniform(4, 6)
               bullets.append(bullet)


       elif entity.type == 2:  # tank - ground e chole ar shoot kore
           entity.position[0] += entity.direction[0] * entity.speed
           entity.position[2] += entity.direction[2] * entity.speed


           if abs(entity.position[0]) > arena_size / 2:
               entity.direction[0] *= -1
           if abs(entity.position[2]) > arena_size / 2:
               entity.direction[2] *= -1


           if time.time() > entity.next_shot_time:
               dx = player_pos[0] - entity.position[0]
               dy = player_pos[1] - entity.position[1]
               dz = player_pos[2] - entity.position[2]
               mag = math.sqrt(dx * dx + dy * dy + dz * dz)
               if mag > 0:
                   dx, dy, dz = dx / mag, dy / mag, dz / mag
               # tank purple bullet fire kore, high damage
               bullets.append(Bullet(
                   entity.position[0], entity.position[1] + 1, entity.position[2],
                   dx, dy, dz, player_bullet=False, damage=5, color=(0.5, 0.0, 0.5)  # purple
               ))
               entity.next_shot_time = time.time() + random.uniform(3, 7)


       elif entity.type == 3:  # shield
           dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(entity.position, player_pos)))
           if dist < 2:
               player_shield_active = True
               player_shield_end_time = time.time() + shield_duration
               entities.remove(entity)


       elif entity.type == 4:  # medbox
           dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(entity.position, player_pos)))
           if dist < 2:
               player_health = min(player_health + 25, max_player_health)
               entities.remove(entity)


   # bullet collision check kora
   for bullet in bullets[:]:
       # drone bullet er jonno drone_bullet_speed use kora
       speed = drone_bullet_speed if not bullet.player_bullet else bullet_speed
       bullet.position[0] += bullet.direction[0] * speed
       bullet.position[1] += bullet.direction[1] * speed
       bullet.position[2] += bullet.direction[2] * speed


       if (abs(bullet.position[0]) > arena_size / 2 or
           bullet.position[1] < 0 or bullet.position[1] > 20 or
           abs(bullet.position[2]) > arena_size / 2):
           bullets.remove(bullet)
           continue


       if bullet.player_bullet:
           for entity in entities[:]:
               dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(entity.position, bullet.position)))
               if dist < 1.5:  # bullet entity te hit koreche
                   entity.health -= bullet.damage
                   bullets.remove(bullet)
                   if entity.health <= 0:
                       if entity.type == 2:
                           tanks_killed += 1
                           score += 50
                       elif entity.type == 1:
                           megatron_killed += 1
                           score += 100
                       elif entity.type == 0:
                           score += 10
                       entities.remove(entity)
                   break
       else:
           # player er sath collision check
           dist = math.sqrt(
               (player_pos[0] - bullet.position[0])**2 +
               (player_pos[1] - bullet.position[1])**2 +
               (player_pos[2] - bullet.position[2])**2
           )
           if dist < 1.5:  # collision threshold
               player_health -= bullet.damage
               bullets.remove(bullet)
               # player health 0 er niche na jaye
               player_health = max(player_health, 0)


def update_player():
   global player_pos
   yaw = player_rot[1] * math.pi / 180.0
   forward = [math.sin(yaw), 0, math.cos(yaw)]
   right = [math.cos(yaw), 0, -math.sin(yaw)]
   if keys['w']:
       player_pos[0] += forward[0] * player_speed
       player_pos[2] += forward[2] * player_speed
   if keys['s']:
       player_pos[0] -= forward[0] * player_speed
       player_pos[2] -= forward[2] * player_speed
   if keys['a']:
       player_pos[0] -= right[0] * player_speed
       player_pos[2] -= right[2] * player_speed
   if keys['d']:
       player_pos[0] += right[0] * player_speed
       player_pos[2] += right[2] * player_speed
   player_pos[0] = max(min(player_pos[0], arena_size/2-1), -arena_size/2+1)
   player_pos[2] = max(min(player_pos[2], arena_size/2-1), -arena_size/2+1)


def update():
   global last_spawn_time_tank_red, last_spawn_time_blue, last_spawn_time_medbox, last_spawn_time_shield, gun_level, paused
   if paused:
       return
   if player_health <= 0:  # health 0 or kom hole game over
       game_over()
       return
   update_player()
   update_entities()
   # score er upor gun level update: 100 point e 1 level barbe
   gun_level = (score // 100) + 1


   current_time = time.time()
   if current_time - last_spawn_time_tank_red >= 5.0:
       spawn_tank()
       spawn_red_drone()
       last_spawn_time_tank_red = current_time
   if current_time - last_spawn_time_blue >= 10.0:
       spawn_blue_drone()
       last_spawn_time_blue = current_time
   if current_time - last_spawn_time_medbox >= 10.0:
       spawn_medbox()
       last_spawn_time_medbox = current_time
   if current_time - last_spawn_time_shield >= 10.0:
       spawn_shield()
       last_spawn_time_shield = current_time


def shoot():
   global last_shot_time
   current_time = time.time()
   if current_time - last_shot_time < shot_cooldown:
       return
   last_shot_time = current_time
   pitch = player_rot[0] * math.pi / 180.0
   yaw = player_rot[1] * math.pi / 180.0
   dx = math.sin(yaw) * math.cos(pitch)
   dy = -math.sin(pitch)
   dz = math.cos(yaw) * math.cos(pitch)
   # player er bullet er damage gun_level
   bullets.append(Bullet(
       player_pos[0], player_pos[1], player_pos[2],
       dx, dy, dz, player_bullet=True, damage=gun_level
   ))


def draw_arena():
   glColor3f(0.1, 0.1, 0.6)
   glBegin(GL_QUADS)
   glVertex3f(-arena_size / 2, 0, -arena_size / 2)
   glVertex3f(-arena_size / 2, 0, arena_size / 2)
   glVertex3f(arena_size / 2, 0, arena_size / 2)
   glVertex3f(arena_size / 2, 0, -arena_size / 2)
   glEnd()


def draw_player():
   if not first_person_view:
       glPushMatrix()
       glTranslatef(player_pos[0], player_pos[1], player_pos[2])
       glRotatef(player_rot[1], 0, 1, 0)
       glColor3f(0.1, 0.6, 0.1)
       glutSolidCube(1.0)
       glPushMatrix()
       glTranslatef(0, 0.7, 0)
       glColor3f(0.8, 0.6, 0.4)
       glutSolidSphere(0.3, 10, 10)
       glPopMatrix()
       glPushMatrix()
       glTranslatef(0.4, 0, -0.5)
       glColor3f(0.2, 0.2, 0.2)
       glScalef(0.1, 0.1, 1.0)
       glutSolidCube(1.0)
       glPopMatrix()
       if player_shield_active:
           glColor4f(0.2, 0.8, 1.0, 0.5)
           glutWireSphere(1.5, 10, 10)
       glPopMatrix()


def draw_entities():
   for entity in entities:
       glPushMatrix()
       glTranslatef(entity.position[0], entity.position[1], entity.position[2])
       if entity.type == 0:  # red drone
           glColor3f(1.0, 0.3, 0.3)
           glRotatef(90, 1, 0, 0)
           glutSolidCylinder(0.7, 0.1, 20, 1)
       elif entity.type == 1:  # blue drone
           glColor3f(0.3, 0.3, 1.0)
           glRotatef(90, 1, 0, 0)
           glutSolidCylinder(1.2, 0.2, 20, 1)
       elif entity.type == 2:  # tank
           glColor3f(0.7, 0.7, 0.7)
           glutSolidCube(1.5)
           glPushMatrix()
           glTranslatef(0, 0.75, 0)
           glutSolidSphere(0.5, 10, 10)
           dx = player_pos[0] - entity.position[0]
           dz = player_pos[2] - entity.position[2]
           angle = math.atan2(dx, dz) * 180 / math.pi
           glRotatef(angle, 0, 1, 0)
           glTranslatef(0, 0, -1.0)
           glColor3f(0.6, 0.6, 0.6)
           glScalef(0.2, 0.2, 1.0)
           glutSolidCube(1.0)
           glPopMatrix()
       elif entity.type == 3:  # shield
           glColor3f(0.0, 0.9, 0.9)
           glEnable(GL_BLEND)
           glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
           glutSolidSphere(1.0, 20, 20)
           glDisable(GL_BLEND)
       elif entity.type == 4:  # medbox
           glColor3f(1.0, 0.0, 0.0)
           glutSolidCube(1.0)
           glColor3f(1.0, 1.0, 1.0)
           glBegin(GL_QUADS)
           glVertex3f(-0.2, 0.1, 0.51)
           glVertex3f(0.2, 0.1, 0.51)
           glVertex3f(0.2, -0.1, 0.51)
           glVertex3f(-0.2, -0.1, 0.51)
           glEnd()
           glBegin(GL_QUADS)
           glVertex3f(-0.2, 0.1, -0.51)
           glVertex3f(0.2, 0.1, -0.51)
           glVertex3f(0.2, -0.1, -0.51)
           glVertex3f(-0.2, -0.1, -0.51)
           glEnd()
           glBegin(GL_QUADS)
           glVertex3f(-0.51, 0.1, 0.2)
           glVertex3f(-0.51, 0.1, -0.2)
           glVertex3f(-0.51, -0.1, -0.2)
           glVertex3f(-0.51, -0.1, 0.2)
           glEnd()
           glBegin(GL_QUADS)
           glVertex3f(0.51, 0.1, 0.2)
           glVertex3f(0.51, 0.1, -0.2)
           glVertex3f(0.51, -0.1, -0.2)
           glVertex3f(0.51, -0.1, 0.2)
           glEnd()
       glPopMatrix()


def draw_bullets():
   for bullet in bullets:
       glPushMatrix()
       glTranslatef(bullet.position[0], bullet.position[1], bullet.position[2])
       if bullet.player_bullet:
           glColor3f(1.0, 1.0, 0.0)
       else:
           glColor3f(bullet.color[0], bullet.color[1], bullet.color[2])
       glutSolidSphere(0.2, 8, 8)
       glPopMatrix()


# draw_hud modify kora jate time survived pause er somoy freeze hoy
def draw_hud():
   glMatrixMode(GL_PROJECTION)
   glPushMatrix()
   glLoadIdentity()
   glOrtho(0, window_width, 0, window_height, -1, 1)
   glMatrixMode(GL_MODELVIEW)
   glPushMatrix()
   glLoadIdentity()
   glDisable(GL_LIGHTING)
   glDisable(GL_DEPTH_TEST)
   # top left e health bar draw kora
   glColor3f(1.0, 0.0, 0.0)
   glBegin(GL_QUADS)
   glVertex2f(10, window_height - 20)
   glVertex2f(10 + (player_health / max_player_health) * 200, window_height - 20)
   glVertex2f(10 + (player_health / max_player_health) * 200, window_height - 10)
   glVertex2f(10, window_height - 10)
   glEnd()
   if player_shield_active:
       remaining = player_shield_end_time - time.time()
       glColor3f(0.2, 0.8, 1.0)
       glBegin(GL_QUADS)
       glVertex2f(10, window_height - 40)
       glVertex2f(10 + (remaining / shield_duration) * 200, window_height - 40)
       glVertex2f(10 + (remaining / shield_duration) * 200, window_height - 30)
       glVertex2f(10, window_height - 30)
       glEnd()
   glColor3f(1.0, 1.0, 1.0)
   # hud stats
   glRasterPos2f(window_width - 180, window_height - 20)
   draw_string(f"Score: {score}")
   glRasterPos2f(window_width - 180, window_height - 40)
   draw_string(f"Tanks Killed: {tanks_killed}")
   glRasterPos2f(window_width - 180, window_height - 60)
   draw_string(f"Megatrons Killed: {megatron_killed}")
   # time survived display
   if game_end_time is not None:
       # game over hole game_end_time use kora
       time_survived = int(game_end_time - game_start_time)
   elif paused and pause_time is not None:
       # pause hole pause er time use kora
       time_survived = int(pause_time - game_start_time)
   else:
       time_survived = int(time.time() - game_start_time)
   glRasterPos2f(window_width // 2 - 50, window_height - 20)
   draw_string(f"Time Survived: {time_survived}s")
   # time survived er niche gun level show
   glRasterPos2f(window_width // 2 - 50, window_height - 40)
   draw_string(f"Gun Level: {gun_level}")
   glEnable(GL_DEPTH_TEST)
   glEnable(GL_LIGHTING)
   glMatrixMode(GL_PROJECTION)
   glPopMatrix()
   glMatrixMode(GL_MODELVIEW)
   glPopMatrix()


def draw_string(s):
   for c in s:
       glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))


def display():
   glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
   glMatrixMode(GL_MODELVIEW)
   glLoadIdentity()
   if first_person_view:
       gluLookAt(
           player_pos[0], player_pos[1], player_pos[2],
           player_pos[0] + math.sin(player_rot[1] * math.pi / 180.0) * math.cos(player_rot[0] * math.pi / 180.0),
           player_pos[1] - math.sin(player_rot[0] * math.pi / 180.0),
           player_pos[2] + math.cos(player_rot[1] * math.pi / 180.0) * math.cos(player_rot[0] * math.pi / 180.0),
           0, 1, 0
       )
   else:
       camera_distance = 5
       camera_x = player_pos[0] - math.sin(player_rot[1] * math.pi / 180.0) * camera_distance * math.cos(player_rot[0] * math.pi / 180.0)
       camera_y = player_pos[1] + 2 + math.sin(player_rot[0] * math.pi / 180.0) * camera_distance
       camera_z = player_pos[2] - math.cos(player_rot[1] * math.pi / 180.0) * camera_distance * math.cos(player_rot[0] * math.pi / 180.0)
       gluLookAt(
           camera_x, camera_y, camera_z,
           player_pos[0], player_pos[1], player_pos[2],
           0, 1, 0
       )
   draw_arena()
   draw_player()
   draw_entities()
   draw_bullets()
   draw_hud()


   # health 0 or kom hole screen er majhe "game over" show
   if player_health <= 0:
       glColor3f(1.0, 1.0, 1.0)
       glMatrixMode(GL_PROJECTION)
       glPushMatrix()
       glLoadIdentity()
       glOrtho(0, window_width, 0, window_height, -1, 1)
       glMatrixMode(GL_MODELVIEW)
       glPushMatrix()
       glLoadIdentity()
       glRasterPos2f(window_width // 2 - 90, window_height // 2)
       for c in "GAME OVER":
           glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))
       glPopMatrix()
       glMatrixMode(GL_PROJECTION)
       glPopMatrix()


   glutSwapBuffers()


def reshape(width, height):
   global window_width, window_height
   window_width, window_height = width, height
   glViewport(0, 0, width, height)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   gluPerspective(45, width / height, 0.1, 200)
   glMatrixMode(GL_MODELVIEW)


def reset_game():
   global player_pos, player_rot, player_health, player_shield_active, player_shield_end_time
   global entities, bullets, score, game_start_time, last_spawn_time, paused, tanks_killed, megatron_killed
   player_pos = [0, 1, 0]
   player_rot = [0, 0]
   player_health = max_player_health
   player_shield_active = False
   player_shield_end_time = 0
   entities = []
   bullets = []
   score = 0
   tanks_killed = 0
   megatron_killed = 0
   game_start_time = time.time()
   last_spawn_time = time.time()
   paused = False
   spawn_entity()
   spawn_entity()


# keyboard callback modify kora jate pause hole input ignore kore
def keyboard(key, x, y):
   global keys, first_person_view, paused, pause_time, game_start_time, game_end_time
   # 'p' always handle kore pause toggle korar jonno (game over na hole)
   if key == b'p':
       if game_end_time is None:
           if not paused:
               paused = True
               pause_time = time.time()  # pause e time freeze
           else:
               paused = False
               # game_start_time adjust kora jate time counter thik thake
               game_start_time += time.time() - pause_time
               pause_time = None
       return


   # game pause ba over hole baki input ignore
   if paused:
       return


   if key == b'w':
       keys['w'] = True
   elif key == b'a':
       keys['a'] = True
   elif key == b's':
       keys['s'] = True
   elif key == b'd':
       keys['d'] = True
   elif key == b' ':
       keys['space'] = True
       shoot()
   elif key == b'v':
       first_person_view = not first_person_view
   elif key == b'e':
       print(f"Game Ended! Your score: {score}")
       glutLeaveMainLoop()
   elif key == b'q' or key == b'\x1b':
       glutLeaveMainLoop()


def keyboard_up(key, x, y):
   global keys
   if paused:
       return
   if key == b'w':
       keys['w'] = False
   elif key == b'a':
       keys['a'] = False
   elif key == b's':
       keys['s'] = False
   elif key == b'd':
       keys['d'] = False
   elif key == b' ':
       keys['space'] = False


def mouse(button, state, x, y):
   global mouse_x, mouse_y
   mouse_x, mouse_y = x, y
   if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
       shoot()


def motion(x, y):
   global mouse_x, mouse_y, player_rot
   dx = x - mouse_x
   dy = y - mouse_y
   player_rot[1] += dx * mouse_sensitivity
   player_rot[0] += dy * mouse_sensitivity
   player_rot[0] = max(min(player_rot[0], 90), -90)
   while player_rot[1] > 360:
       player_rot[1] -= 360
   while player_rot[1] < 0:
       player_rot[1] += 360
   mouse_x, mouse_y = x, y
   if x < 50 or x > window_width - 50 or y < 50 or y > window_height - 50:
       glutWarpPointer(window_width // 2, window_height // 2)
       mouse_x, mouse_y = window_width // 2, window_height // 2


def timer(value):
   update()
   glutPostRedisplay()
   glutTimerFunc(16, timer, 0)


def game_over():
   global paused, game_end_time
   print(f"Game Over! Your score: {score}")
   paused = True
   game_end_time = time.time()  # game end er time store
   # mouse input disable kora
   glutMouseFunc(lambda button, state, x, y: None)
   glutMotionFunc(lambda x, y: None)
   glutPassiveMotionFunc(lambda x, y: None)
   # mouse cursor show kora
   glutSetCursor(GLUT_CURSOR_LEFT_ARROW)


def main():
   glutInit()
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
   glutInitWindowSize(window_width, window_height)
   glutCreateWindow(b"Neon Defender")


   init()


   glutDisplayFunc(display)
   glutReshapeFunc(reshape)
   glutKeyboardFunc(keyboard)
   glutKeyboardUpFunc(keyboard_up)
   glutMouseFunc(mouse)
   glutMotionFunc(motion)
   glutPassiveMotionFunc(motion)
   glutTimerFunc(16, timer, 0)


   # mouse cursor hide ar capture
   glutSetCursor(GLUT_CURSOR_NONE)


   # mouse initially center e
   glutWarpPointer(window_width // 2, window_height // 2)
   mouse_x, mouse_y = window_width // 2, window_height // 2


   glutMainLoop()


if __name__ == "__main__":
   main()