import pygame as pg
from pygame.locals import *
import math, os, sys
from random import randint
import constants

class Spritesheet:
    def __init__(self, filename, bgColor):
        filename = os.path.join('resources','images','spritesheets',filename)
        self._spritesheet = pg.image.load(filename).convert()
        self.backgroundColor = bgColor

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.set_colorkey(self.backgroundColor)
        image.blit(self._spritesheet, (0, 0), (x, y, width, height))
        return image

class Butterfly(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.spritesheet = Spritesheet('butterfly.png', constants.WHITE)
        self.animation = self.load_animation()
        self.liveframes = 0
        self.game = game
        self.image = self.animation[self.liveframes % len(self.animation)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = randint(0,359)
        self.type = "butterfly"
        self.x = x
        self.y = y
        self.speed = 1.5

    def load_animation(self):
        f1 = self.spritesheet.get_image(0, 0, 16, 16)
        f2 = self.spritesheet.get_image(16, 0, 16, 16)
        f3 = self.spritesheet.get_image(32, 0, 16, 16)
        animation = [f1, f1, f2, f2, f3, f3, f3, f2, f2]
        return animation

    def update(self):
        self.liveframes += 1
        self.direction += randint(-30,30)
        if self.direction < 0:
            self.direction += 360
        elif self.direction >= 360:
            self.direction -= 360
        rad = math.radians(self.direction)
        yAdjust = math.sin(rad) * self.speed * -1
        xAdjust = math.cos(rad) * self.speed
        self.x += xAdjust
        self.y += yAdjust
        
        if self.x < -16:
            self.x += 216
        elif self.x > 200:
            self.x -= 216
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.image = self.animation[self.liveframes % len(self.animation)].copy()
        self.image = pg.transform.rotate(self.image, self.direction)


class Background(pg.sprite.Sprite):
    def __init__(self, filename, yPlacement):
        super().__init__()
        self.image = pg.image.load(os.path.join('resources','images','backgrounds',filename))
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = yPlacement

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill(constants.PURPLE)
        self.has_texture = False
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = "platform"

class Spike(pg.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        super().__init__()
        self.game = game
        self.direction = direction
        rotation_guide = {"N" : 0, "W" : 90, "S" : 180, "E" : 270}
        self.image = pg.image.load(os.path.join('resources','images','spike_{}.png'.format(direction))).convert()
        self.image.set_colorkey(constants.WHITE)
        self.rect = self.image.get_rect()
        self.type = "spike"
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class PhysicsObject(pg.sprite.Sprite):
    def __init__(self, game, x, y , width, height):
        super().__init__()
        self.game = game

    def update_position(self, posAdjustment, walls):
        '''Moves the object (updates rect) within the confines of the walls, returns dict collision_directions
        @param walls: a sprite.Group containing all platforms currently loaded'''

        #Assume no collisions
        collision_directions  = {'top':False, 'bottom':False,
                                 'right':False, 'left':False}

        #Update horizontal position
        self.x += posAdjustment[0]
        self.hitbox.x = int(self.x)
        self.rect.x = int(self.x)-4

        #Check for collisions after horizontal movement
        collisions = self.list_collisions(walls)
        for wall in collisions:

            #If we were moving towards the right, adjust the rightmost edge of
            #our Rect to align with the leftmost edge of the wall
            if posAdjustment[0] > 0:
                self.hitbox.right = wall.rect.left
                collision_directions['right'] = True
            elif posAdjustment[0] < 0:
                self.hitbox.left = wall.rect.right
                collision_directions['left'] = True

            #Update self.x after collision adjustment
            self.x = self.hitbox.x
            self.rect.x = self.x-4
                
        #Update vertical position
        self.y += posAdjustment[1]
        self.hitbox.y = int(self.y)
        self.rect.y = int(self.y)-2

        #Check for collisions again after vertical movement
        collisions = self.list_collisions(walls)
        for wall in collisions:
            if posAdjustment[1] > 0:
                self.hitbox.bottom = wall.rect.top
                collision_directions['bottom'] = True
            else:
                self.hitbox.top = wall.rect.bottom
                collision_directions['top'] = True

            self.y = self.hitbox.y
            self.rect.y = self.y-2

        return collision_directions

    def list_collisions(self, walls):
        collisions = []
        for wall in walls:
            if wall.rect.colliderect(self.hitbox):
                collisions.append(wall)
        return collisions

##    def list_collisions(self, walls):
##        collisions = pg.sprite.spritecollide(self, walls, False, pg.sprite.collide_mask)
##        return collisions

class Bomb(PhysicsObject):
    def __init__(self, game, x, y, width, height, hspeed, vspeed):
        super().__init__(game, x, y, width, height)
        self.game = game
        self.spritesheet = Spritesheet("bomb.png", constants.WHITE)
        self.animations = self.load_animations()
        self.image = self.animations['preboom'][0]
        self.currentAnimation = "preboom"
        self.rect = self.image.get_rect()
        self.rect.x = x-4
        self.rect.y = y-2
        self.hitbox = Rect(x, y, self.rect.width-8, self.rect.height-4)
        self.type = "bomb"
        self.x = x
        self.y = y
        self.lifespan = 2*(len(self.animations['preboom'])+len(self.animations['postboom']))
        self.hspeed = hspeed
        self.vspeed = vspeed
        if vspeed > 0:
            self.vspeed = 0
        if not self.game.down_pressed:
            self.vspeed -= 4
        self.sound_boom = pg.mixer.Sound(os.path.join('resources', 'sounds', 'boom.wav'))

    def update(self):
        if self.lifespan > 2*len(self.animations["postboom"]):
            self.vspeed += constants.GRAVITY
        if self.vspeed > 15:
            self.vspeed = 15
        self.hspeed *= 0.97

        collision_directions = self.update_position([self.hspeed, self.vspeed], self.game.platforms)
        if collision_directions['bottom']:
            self.vspeed = 0
        elif collision_directions['right'] or collision_directions['left']:
            self.hspeed = 0

        if self.lifespan == 0:
            self.kill()
        if self.lifespan > 2*len(self.animations["postboom"]): #if lifespan > 30
            self.image = self.animations["preboom"][len(self.animations["preboom"])-(self.lifespan - 2*len(self.animations['postboom']))//2-1]
        elif self.lifespan == 2*len(self.animations["postboom"]):
            self.explode()
        else:
            self.image = self.animations["postboom"][len(self.animations["postboom"])-self.lifespan//2-1]
        self.lifespan -= 1

    def explode(self):

        self.hspeed = 0
        self.vspeed = 0

        explosionZone = Rect(self.rect.left-5, self.rect.top-5, self.rect.width+10, self.rect.width+10)
        for spike in self.game.spikes:
            if spike.rect.colliderect(explosionZone):
                spike.kill()
                self.game.spikes.remove(spike)

        self.sound_boom.play()
        
    def load_animations(self):
        '''returns a dictionary of lists, each list an animation cycle'''
        animations = {}
        pb1 = self.spritesheet.get_image(0, 0, 20, 20)
        pb2 = self.spritesheet.get_image(20, 0, 20, 20)
        pb3 = self.spritesheet.get_image(0, 20, 20, 20)
        pb4 = self.spritesheet.get_image(20, 20, 20, 20)
        pb5 = self.spritesheet.get_image(0, 40, 20, 20)
        pb6 = self.spritesheet.get_image(20, 40, 20, 20)
        animations['preboom'] = [pb1]*4 + [pb2]*4 + [pb3]*4 + [pb4]*4 + [pb5]*4 + [pb6]*4
        pob1 = self.spritesheet.get_image(60, 40, 20, 20)
        pob2 = self.spritesheet.get_image(40, 40, 20, 20)
        pob3 = self.spritesheet.get_image(60, 20, 20, 20)
        pob4 = self.spritesheet.get_image(40, 20, 20, 20)
        pob5 = self.spritesheet.get_image(60, 0, 20, 20)
        pob6 = self.spritesheet.get_image(40, 0, 20, 20)
        animations['postboom'] = [pob2, pob2, pob1, pob1, pob1, pob2, pob2,
                                  pob3, pob3, pob4, pob4, pob5, pob5, pob6, pob6]
        return animations
        

class Player(PhysicsObject):
    def __init__(self, game, x, y, width, height):
        super().__init__(game, x, y, width, height)
        self.spritesheet = Spritesheet("player.png", constants.PLAYER_BG)
        self.animations = self.load_animations()
        self.game = game
        self.image = self.spritesheet.get_image(16, 478, 16, 24)
        self.hitbox = Rect(x, y, 8, 19)
##        self.mask = pg.mask.Mask((16,24))
##        self.mask.fill()
        self.currentAnimation = 'standing'
        self.rect = self.image.get_rect()
        self.rect.x = x-4
        self.rect.y = y-2
        self.type = "player"
        self.x = x
        self.y = y
        self.grounded = False
        self.airtime = 0
        self.vspeed = 0
        self.hspeed = 0
        self.debugTick = 0
        self.canDropBomb = True
        self.sound_jump = pg.mixer.Sound(os.path.join('resources','sounds','jump.wav'))

    def update(self):
        '''Update the player's position and animation'''

        #Gravity, speed caps
        if not self.grounded:
            self.vspeed += constants.GRAVITY
        if self.vspeed > 8:
            self.vspeed = 8

        #Key input / controls
        if self.game.right_pressed:
            self.hspeed += 2
            if self.grounded:
                self.currentAnimation = 'walking'
        if self.game.left_pressed:
            self.hspeed -= 2
            if self.grounded:
                self.currentAnimation = 'walking'
        if self.game.up_pressed:
            if self.grounded:
                self.grounded = False
                self.vspeed = -4
                self.sound_jump.play()
                self.currentAnimation = 'jumping'
            elif self.vspeed < 0:
                self.vspeed -= 0.2
        if self.game.space_pressed and self.canDropBomb:
            bomb = Bomb(self.game, self.rect.x, self.rect.y, 20, 20, self.hspeed, self.vspeed)
            self.game.allSprites.add(bomb)
            butt = Butterfly(self.game, self.x, self.y)
            self.game.allSprites.add(butt, layer=2)
            self.canDropBomb = False
        if not self.game.space_pressed:
            self.canDropBomb = True

        collision_directions = self.update_position([self.hspeed, self.vspeed], self.game.platforms)
        if collision_directions['bottom']:
            self.grounded = True
            self.vspeed = 0
        else:
            if not self.thereIsGroundBeneathMe():
                self.grounded = False

        if self.hitbox.y > constants.SCROLL_HEIGHT:
            self.game.scrollLength += self.hitbox.y - constants.SCROLL_HEIGHT
            for _ in range(int(self.game.scrollLength) // 20 - self.game.rows_killed):
                self.game.rows.pop(0)
                self.game.rows_killed += 1
            for sprite in self.game.allSprites:
                if sprite != self:
                    sprite.rect.y -= self.hitbox.y - constants.SCROLL_HEIGHT
                if sprite.type in ("butterfly", "bomb"):
                    sprite.y -= self.hitbox.y - constants.SCROLL_HEIGHT
                if sprite.rect.bottom < 0:
                    if sprite.type == "spike":
                       self.game.spikes.remove(sprite)
                    elif sprite.type == "platform":
                        self.game.platforms.remove(sprite)
                    sprite.kill()
            self.hitbox.y = constants.SCROLL_HEIGHT
            self.y = self.hitbox.y
            self.rect.y = self.y-2

        #Player animation
        if self.currentAnimation != 'standing' and self.grounded and self.hspeed == 0:
            self.currentAnimation = 'standing'
        if self.vspeed > 0 and not self.thereIsGroundBeneathMe():
            self.currentAnimation = 'falling'

        self.image = self.animations[self.currentAnimation]\
                     [(self.game.ticks_passed // 2) % len(self.animations[self.currentAnimation])]
        if self.game.left_pressed:
            self.image = pg.transform.flip(self.image, True, False)
        elif not self.game.right_pressed and self.currentAnimation in ('jumping', 'falling'):
            self.image = self.animations['jumpingstraight'][0]

        self.hspeed = 0
        #Check if we've collided with a spike
        self.die_if_spikes()

    def die_if_spikes(self):
        for spike in self.game.spikes:
            if spike.rect.colliderect(self.hitbox):
                triggered = False
                if spike.direction == "N" and self.vspeed > 0:
                    triggered = True
                if spike.direction == "W" and self.hspeed > 0:
                    triggered = True
                if spike.direction == "S" and self.vspeed < 0:
                    triggered = True
                if spike.direction == "E" and self.hspeed < 0:
                    triggered = True
                if triggered:
                    self.game.isalive = False

    def load_animations(self):
        '''returns a dictionary of lists, each list an animation cycle'''
        animations = {}
        animations['standing'] = [self.spritesheet.get_image(16, 478, 16, 24)]
        w1 = self.spritesheet.get_image(86, 439, 16, 24)
        w2 = self.spritesheet.get_image(104, 439, 16, 24)
        w3 = self.spritesheet.get_image(122, 439, 16, 24)
        animations['walking'] = [w2, w2, w2, w3, w3, w3, w3, w2, w2, w2, w1, w1, w1, w1]
        jUp = self.spritesheet.get_image(308, 439, 16, 24)
        jDown = self.spritesheet.get_image(332, 439, 16, 24)
        jStraight = self.spritesheet.get_image(290, 465, 16, 24)
        animations['jumping'] = [jUp]
        animations['jumpingstraight'] = [jStraight]
        animations['falling'] = [jDown]
        i1 = self.spritesheet.get_image(86, 465, 16, 24)
        animations['idle1'] = [i1, i1, i1, i1, i1, i1, i1, i1, i1, i1, i1]

        return animations

    def spawnDeadFox(self):
        dead_img = self.spritesheet.get_image(152, 491, 16, 24)

    def thereIsGroundBeneathMe(self):
        slightlyLower = pg.Rect(self.hitbox.left, self.hitbox.top+1, self.hitbox.width, self.hitbox.height)
        for wall in self.game.platforms:
            if wall.rect.colliderect(slightlyLower):
                return True
        return False

        
