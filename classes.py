import pygame as pg
from pygame.locals import *
import math, os
import constants

class Spritesheet:
    def __init__(self, filename):
        self._spritesheet = pg.image.load(filename)

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.set_colorkey(constants.PLAYER_BG)
        image.blit(self._spritesheet, (0, 0), (x, y, width, height))
        return image

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill(constants.PURPLE)
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
        collisions = self.list_collisions(walls)
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
        collisions = self.list_collisions(walls)
        for wall in collisions:
            if posAdjustment[1] > 0:
                self.rect.bottom = wall.rect.top
                collision_directions['bottom'] = True
            else:
                self.rect.top = wall.rect.bottom
                collision_directions['top'] = True

            self.y = self.rect.y

        return collision_directions

    def list_collisions(self, walls):
        collisions = []
        for wall in walls:
            if wall.rect.colliderect(self.rect):
                collisions.append(wall)
        return collisions
        

class Player(PhysicsObject):
    def __init__(self, game, x, y, width, height):
        super().__init__(game, x, y, width, height)
        self.spritesheet = Spritesheet(os.path.join("resources", "images", "player.png"))
        self.animations = self.load_animations()
        self.game = game
        self.image = self.spritesheet.get_image(16, 478, 16, 24)
        self.currentAnimation = 'standing'
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
        self.vspeed += constants.GRAVITY
        if self.vspeed > 8:
            self.vspeed = 8
        self.hspeed = 0

        #Key input / controls
        if self.game.right_pressed == True:
            self.hspeed += 2
            if self.grounded:
                self.currentAnimation = 'walking'
        if self.game.left_pressed == True:
            self.hspeed -= 2
            if self.grounded:
                self.currentAnimation = 'walking'
        if self.game.up_pressed == True:
            if self.grounded:
                self.grounded = False
                self.vspeed = -4
                self.sound_jump.play()
                self.currentAnimation = 'jumping'
            elif self.vspeed < 0:
                self.vspeed -= 0.2
            
        collision_directions = self.update_position([self.hspeed, self.vspeed], self.game.platforms)
        if collision_directions['bottom']:
            self.grounded = True
            self.vspeed = 0
        else:
            if not self.thereIsGroundBeneathMe():
                self.grounded = False
        if collision_directions['top']:
            self.vspeed = 0

        if self.rect.y > constants.SCROLL_HEIGHT:
            self.game.scrollLength += self.rect.y - constants.SCROLL_HEIGHT
            for _ in range(int(self.game.scrollLength) // 20 - self.game.rows_killed):
                self.game.rows.pop(0)
                self.game.rows_killed += 1
            for sprite in self.game.allSprites:
                if sprite != self:
                    sprite.rect.y -= self.rect.y - constants.SCROLL_HEIGHT
                if sprite.rect.bottom < 0:
                    sprite.kill()
            self.rect.y = constants.SCROLL_HEIGHT
            self.y = self.rect.y

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

    def thereIsGroundBeneathMe(self):
        slightlyLower = pg.Rect(self.rect.left, self.rect.top+1, self.rect.width, self.rect.height)
        for wall in self.game.platforms:
            if wall.rect.colliderect(slightlyLower):
                return True
        return False

        
