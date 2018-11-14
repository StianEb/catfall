###
#
# TODO:

# - Give limited number of bombs at start, display it somehow
# - Add a score counter, keep highscore in file
# - Add a death animation and a restart screen / function
# - Add a background
# - Would be nice: Powerups (More bombs, T-shirt)
# - Would also be nice: More enemies / obstacles, more skill-based gameplay

import pygame as pg
from pygame.locals import *
from constants import *
from classes import *
import sys, os
from random import randint

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.init()

        pg.mixer.music.load(os.path.join('resources','sounds','Chibi Ninja (Eric Skiff).wav'))
        pg.mixer.music.play(-1)

        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.truescreen = pg.Surface((200, 300))
        pg.display.set_caption("CatFall")
        self.tilebook = self.initialize_tilebook()


    def start(self):
        self.allSprites = pg.sprite.LayeredUpdates()
        self.luck = 0
        self.spikes = []
        self.rows = []
        self.scrollLength = 0
        self.rows_killed = 0
        self.ticks_passed = 0
        self.backgroundsSpawned = 0

        #Controls
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False
        self.platforms = []

        self.player = Player(self, WINDOW_WIDTH//12, WINDOW_HEIGHT//12, 16, 24)
        self.allSprites.add(self.player, layer=-2)

        self.load_starting_section()
        for rowNumber in range(len(self.rows)):
            self.spawn_row_of_platforms(rowNumber)
        for _ in range(len(self.rows)-1):
            self.texture_next_row_of_tiles()
        
        self.run()

    def run(self):
        self.alive = True
        while self.alive:
            self.clock.tick(60)
            self.ticks_passed += 1
            self.events()
            self.update()
            self.draw()
        self.gameover()

    def gameover(self):
        print("Game over!")

    def events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    self.right_pressed = True
                if event.key == K_LEFT:
                    self.left_pressed = True
                if event.key == K_UP:
                    self.up_pressed = True
                if event.key == K_DOWN:
                    self.down_pressed = True
                if event.key == K_SPACE:
                    self.space_pressed = True
            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.right_pressed = False
                if event.key == K_LEFT:
                    self.left_pressed = False
                if event.key == K_UP:
                    self.up_pressed = False
                if event.key == K_DOWN:
                    self.down_pressed = False
                if event.key == K_SPACE:
                    self.space_pressed = False

    def update(self):
        self.allSprites.update() #runs .update() on all objects in allSprites

        if len(self.rows) <= 16:
            self.load_new_section()
            
    def draw(self):
        self.truescreen.fill(LIGHT_BLUE)
        self.allSprites.draw(self.truescreen)
        self.screen.blit(pg.transform.scale(self.truescreen, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
        pg.display.flip()

    def load_section_into_rows(self, sectionName):
        sectionPath = os.path.join('resources', 'images', 'sections', 'section_{}.png'.format(sectionName))
        sectionSurface = pg.image.load(sectionPath).convert_alpha()
        height = sectionSurface.get_height()
        
        for y in range(height):
            self.rows.append([])
            for x in range(sectionSurface.get_width()):
                if sectionSurface.get_at((x, y))[:3] == (0, 0, 0):
                    self.rows[-1].append(x)

        return height

    def spawn_row_of_platforms(self, row):
        if self.platforms:
            yPos = self.platforms[-1].rect.bottom
        else:
            yPos = 0
        
        for xPosition in self.rows[row]:
            platform = Platform(20*xPosition, yPos, 20, 20)
            self.platforms.append(platform)
            self.allSprites.add(platform)

    def load_starting_section(self):
        self.load_section_into_rows("start")

    def load_new_section(self):
        
        oldrowsLoaded = len(self.rows)
        sectionNumber = randint(1,13)
        height = self.load_section_into_rows(str(sectionNumber))
        rowsLoaded = len(self.rows)
        for i in range(height):
            rowToSpawn = rowsLoaded-height+i
            self.spawn_row_of_platforms(rowToSpawn)

        for _ in range(rowsLoaded - oldrowsLoaded):
            self.texture_next_row_of_tiles()

    def initialize_tilebook(self):
        soil_tiles = Spritesheet('soil-tiles.png', constants.BLACK)
        tilebook = {}
        tilebook['soil'] = {}
        tilebook['soil']['alone'] = soil_tiles.get_image(0, 0, 20, 20)
        tilebook['soil']['N'] = soil_tiles.get_image(60, 60, 20, 20)
        tilebook['soil']['E'] = soil_tiles.get_image(20, 0, 20, 20)
        tilebook['soil']['S'] = soil_tiles.get_image(60, 20, 20, 20)
        tilebook['soil']['W'] = soil_tiles.get_image(60, 0, 20, 20)
        tilebook['soil']['NE'] = soil_tiles.get_image(0, 60, 20, 20)
        tilebook['soil']['NS'] = soil_tiles.get_image(60, 40, 20, 20)
        tilebook['soil']['NW'] = soil_tiles.get_image(40, 60, 20, 20)
        tilebook['soil']['ES'] = soil_tiles.get_image(0, 20, 20, 20)
        tilebook['soil']['EW'] = soil_tiles.get_image(40, 0, 20, 20)
        tilebook['soil']['SW'] = soil_tiles.get_image(40, 20, 20, 20)
        tilebook['soil']['NES'] = soil_tiles.get_image(0, 40, 20, 20)
        tilebook['soil']['NEW'] = soil_tiles.get_image(20, 60, 20, 20)
        tilebook['soil']['NSW'] = soil_tiles.get_image(40, 40, 20, 20)
        tilebook['soil']['ESW'] = soil_tiles.get_image(20, 20, 20, 20)
        tilebook['soil']['NESW'] = soil_tiles.get_image(20, 40, 20, 20)
        tilebook['soil']['corners'] = soil_tiles.get_image(80, 0, 20, 20)
        
        return tilebook
    
    def texture_next_row_of_tiles(self):
        
        for i, plat in enumerate(self.platforms):
            if not plat.has_texture:
                target_elevation = plat.rect.y
                same_level = []
                next_level = []
                previous_level = []
                
                for j in range(i, len(self.platforms)):
                    
                    #Locate all platforms on that row
                    if self.platforms[j].rect.y == target_elevation:
                        same_level.append(self.platforms[j])
                    #Locate the row below
                    elif self.platforms[j].rect.y == target_elevation + plat.rect.height:
                        next_level.append(self.platforms[j])
                    else:
                        break

                if i == 0:
                    previous_level = False
                else:
                    #Locate the row above
                    for k in range(i-1, 0, -1):
                        if self.platforms[k].rect.y == target_elevation - plat.rect.height:
                            previous_level.append(self.platforms[k])
                        else:
                            break

                if not next_level:
                    print("Error: Tried to texture last existing row")
                break
        
        for platform in same_level:
            self.texture_tile(platform, previous_level, same_level, next_level)

    def texture_tile(self, platform, upper, same, lower):
        
        up = False
        upleft = False
        upright = False
        right = False
        left = False
        downleft = False
        down = False
        downright = False

        if platform.rect.x == 0:
            upleft = True
            left = True
            downleft = True
        elif platform.rect.x == 180:
            upright = True
            right = True
            downright = True
        
        if not upper:
            up = True
            upleft = True
            upright = True
        else:
            for plat in upper:
                if plat.rect.x == platform.rect.x:
                    up = True
                elif plat.rect.x == platform.rect.x-20:
                    upleft = True
                elif plat.rect.x == platform.rect.x+20:
                    upright = True

        for plat in same:
            if plat.rect.x == platform.rect.x - platform.rect.width or platform.rect.left == 0:
                left = True
            if plat.rect.x == platform.rect.x + platform.rect.width or platform.rect.left == 180:
                right = True

        for plat in lower:
            if plat.rect.x == platform.rect.x:
                down = True
            elif plat.rect.x == platform.rect.x-20:
                downleft = True
            elif plat.rect.x == platform.rect.x+20:
                downright = True

        texture_ID = ''
        if not (up or right or down or left):
            texture_ID = 'alone'
        if up:
            texture_ID += 'N'
        else:
            self.maybe_spawn_spike(platform.rect.left+2, platform.rect.top-11, "N")
        if right:
            texture_ID += 'E'
        else:
            self.maybe_spawn_spike(platform.rect.right-4, platform.rect.top+2, "E")
        if down:
            texture_ID += 'S'
        else:
            self.maybe_spawn_spike(platform.rect.left+2, platform.rect.bottom-4, "S")
        if left:
            texture_ID += 'W'
        else:
            self.maybe_spawn_spike(platform.rect.left-11, platform.rect.top+2, "W")
            
        img = self.tilebook['soil'][texture_ID].copy()
        if up and left and not upleft:
            img.blit(self.tilebook['soil']['corners'], (0, 0), area=pg.Rect(0, 0, 10, 10))
        if up and right and not upright:
            img.blit(self.tilebook['soil']['corners'], (10, 0), area=pg.Rect(10, 0, 10, 10))
        if down and left and not downleft:
            img.blit(self.tilebook['soil']['corners'], (0, 10), area=pg.Rect(0, 10, 10, 10))
        if down and right and not downright:
            img.blit(self.tilebook['soil']['corners'], (10, 10), area=pg.Rect(10, 10, 10, 10))
        platform.image = img
        platform.has_texture = True
        platform.neighborkey = [upleft, up, upright, left, right, downleft, down, downright]

    def maybe_spawn_spike(self, x, y, direction):
        if randint(1,1000) > 990 - self.scrollLength/100:
            spike = Spike(self, x, y, direction)
            self.allSprites.add(spike, layer=-1)
            self.spikes.append(spike)

def main():
    game = Game()
    while True:
        game.start()

main()
