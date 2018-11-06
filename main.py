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

        if len(self.rows) <= 15:
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
        sectionNumber = randint(1,3)
        self.load_section_into_rows(str(sectionNumber))
        rowsLoaded = len(self.rows)
        for i in range(15):
            rowToSpawn = rowsLoaded-15+i
            self.spawn_row_of_platforms(rowToSpawn)
        

def main():
    game = Game()
    game.start()

main()
