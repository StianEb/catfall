import pygame as pg
from pygame.locals import *
import math, os

from constants import *

##class Spritesheet:
##    def __init__(self, filename):
##        self._spritesheet = pg.image.load(filename)#.convert()
##
##    def get_image(self, x, y, width, height):
##        image = pg.Surface((width, height))
##        image.blit(self._spritesheet, (0, 0), (x, y, width, height))
##        return image


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PhysicsObject(pg.sprite.Sprite):
    def __init__(self, game, x, y , width, height):
        super().__init__()
        self.game = game
        self.x = x #float values
        self.y = y
        
        self.rect = pg.Rect(x, y, width, height)

    def update_position(self, posAdjustment, walls):
        '''Moves the object (updates rect) within the confines of the walls, returns dict collision_directions
        @param walls: a sprite.Group containing all platforms currently loaded'''

        #Assume no collisions
        collision_directions  = {'top':False, 'bottom':False,
                                 'right':False, 'left':False}

        #Update horizontal position
        self.x += posAdjustment[0]
        self.rect.x = int(self.x)

        #Check for collisions after horizontal movement
        collisions = self._list_collisions(walls)
        for wall in collisions:

            #If we were moving towards the right, adjust the rightmost edge of
            #our Rect to align with the leftmost edge of the wall
            if posAdjustment[0] > 0:
                self.rect.right = wall.rect.left
                collision_directions['right'] = True
            elif posAdjustment[0] < 0:
                self.rect.left = wall.rect.right
                collision_directions['left'] = True

            #Update self.x after collision adjustment
            self.x = self.rect.x
                
        #Update vertical position
        self.y += posAdjustment[1]
        self.rect.y = int(self.y)

        #Check for collisions again after vertical movement
        collisions = self._list_collisions(walls)
        for wall in collisions:
            if posAdjustment[1] > 0:
                self.rect.bottom = wall.rect.top
                collision_directions['bottom'] = True
            else:
                self.rect.top = wall.rect.bottom
                collision_directions['top'] = True

            self.y = self.rect.y

        return collision_directions

    def _list_collisions(self, walls):
        collisions = []
        for wall in walls:
            if wall.rect.colliderect(self.rect):
                collisions.append(wall)
        return collisions
        

class Player(PhysicsObject):
    def __init__(self, game, x, y, width, height):
        super().__init__(game, x, y, width, height)
        #self.animations = {'standing': PLAYER_STANDING}
        #self.image = PLAYER_STANDING[0]
        self.game = game
        self.image = pg.Surface((width, height))
        self.image.fill((0,0,145))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.grounded = False
        self.airtime = 0
        self.vspeed = 0
        self.hspeed = 0
        self.debugTick = 0
        self.sound_jump = pg.mixer.Sound(os.path.join('resources','sounds','jump.wav'))

    def update(self):
        '''Update the player's position and animation'''

        #Player movement

        #Gravity, speed caps
        self.vspeed += GRAVITY
        if self.vspeed > 8:
            self.vspeed = 8
        self.hspeed = 0

        #Key input / controls
        if self.game.right_pressed == True:
            self.hspeed += 2
        if self.game.left_pressed == True:
            self.hspeed -= 2
        if self.game.up_pressed == True:
            if self.grounded:
                self.grounded = False
                self.vspeed = -4
                self.sound_jump.play()
            elif self.vspeed < 0:
                self.vspeed -= 0.2
                #p.set_animation(player_jump_anim)
            
        collision_directions = self.update_position([self.hspeed, self.vspeed], self.game.platforms)
        if collision_directions['bottom']:
            self.grounded = True
            self.vspeed = 0
        else:
            self.grounded = False
        if collision_directions['top']:
            self.vspeed = 0

        if self.rect.y > 200:
            self.game.scrollLength += self.rect.y - 200
            for _ in range(int(self.game.scrollLength) // 20 - self.game.rows_killed):
                self.game.rows.pop(0)
                self.game.rows_killed += 1
                print("Rows killed: {}".format(self.game.rows_killed))
                print("Scroll length so far: {}".format(self.game.scrollLength))
            for sprite in self.game.allSprites:
                if sprite != self:
                    sprite.rect.y -= self.rect.y - 200
                if sprite.rect.bottom < 0:
                    sprite.kill()
            self.rect.y = 200
            self.y = 200
