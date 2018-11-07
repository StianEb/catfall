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
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.truescreen = pg.Surface((200, 300))
        pg.display.set_caption("CatFall")
        self.rows = []
        self.scrollLength = 0
        self.rows_killed = 0
        self.running = True
        self.ticks_passed = 0
        self.tilebook = self.initialize_tilebook()

        #Controls
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False
        self.platforms = []

    def start(self):
        self.allSprites = pg.sprite.Group()

        self.player = Player(self, WINDOW_WIDTH//12, WINDOW_HEIGHT//12, 16, 24)
        self.allSprites.add(self.player)

        self.load_starting_section()
        for rowNumber in range(len(self.rows)):
            self.spawn_row_of_platforms(rowNumber)
        for _ in range(len(self.rows)-1):
            self.texture_next_row_of_tiles()
        
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(60)
            self.ticks_passed += 1
            self.events()
            self.update()
            self.draw()

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
            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.right_pressed = False
                if event.key == K_LEFT:
                    self.left_pressed = False
                if event.key == K_UP:
                    self.up_pressed = False

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
        
        for y in range(sectionSurface.get_height()):
            self.rows.append([])
            for x in range(sectionSurface.get_width()):
                if sectionSurface.get_at((x, y))[:3] == (0, 0, 0):
                    self.rows[-1].append(x)

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
        sectionNumber = randint(1,3)
        self.load_section_into_rows(str(sectionNumber))
        rowsLoaded = len(self.rows)
        for i in range(15):
            rowToSpawn = rowsLoaded-15+i
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
        right = False
        down = False
        left = False
        
        if not upper:
            up = True
        else:
            for plat in upper:
                if plat.rect.x == platform.rect.x:
                    up = True

        for plat in same:
            if plat.rect.x == platform.rect.x - platform.rect.width:
                left = True
            elif plat.rect.x == platform.rect.x + platform.rect.width:
                right = True

        for plat in lower:
            if plat.rect.x == platform.rect.x:
                down = True

        texture_ID = ''
        if not (up or right or down or left):
            texture_ID = 'alone'
        if up:
            texture_ID += 'N'
        if right:
            texture_ID += 'E'
        if down:
            texture_ID += 'S'
        if left:
            texture_ID += 'W'
            
        platform.image = self.tilebook['soil'][texture_ID]
        platform.has_texture = True
                    

def main():
    game = Game()
    game.start()

main()
