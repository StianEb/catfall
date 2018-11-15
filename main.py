
import pygame as pg
from pygame.locals import *
import constants
from classes import *
import sys, os, time
from random import randint

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
        self.truescreen = pg.Surface((200, 300))
        pg.display.set_caption("Catfall")
        self.tilebook = self.initialize_tilebook()
        self.allSprites = pg.sprite.LayeredUpdates()
        self.guibook = self.load_icons()
        self.font = pg.font.Font(pg.font.match_font('arial bold'), 40)
        self.deadFox = None
        self.sound_gameover = pg.mixer.Sound(os.path.join('resources', 'sounds', 'game_over.wav'))

    def start(self):

        pg.mixer.music.load(os.path.join('resources','sounds','Chibi Ninja (Eric Skiff).wav'))
        pg.mixer.music.play(-1)
        
        self.luck = 0
        self.butterflies = []
        self.spikes = []
        self.bomb_upgrades = []
        self.rows = []
        self.scrollLength = 0
        self.rows_killed = 0
        self.ticks_passed = 0
        self.maxbombs = 3
        self.bombs = 3
        self.score = 0

        #Controls
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False
        self.platforms = []

        self.player = Player(self, constants.WINDOW_WIDTH//12, constants.WINDOW_HEIGHT//12, 16, 24)
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

        self.score = self.scrollLength // 100
        self.bombs += 0.003
        if self.bombs > self.maxbombs:
            self.bombs = self.maxbombs
            
    def draw(self):
        self.truescreen.fill(constants.LIGHT_BLUE)
        self.allSprites.draw(self.truescreen)
        self.draw_bomb_icons()
        self.screen.blit(pg.transform.scale(self.truescreen, (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)), (0, 0))
        self.draw_score()
        pg.display.flip()

    def gameover(self):
        
        pg.mixer.music.load(os.path.join('resources','sounds','Come and Find Me (Eric Skiff).wav'))
        pg.mixer.music.play(-1)
        self.sound_gameover.play()
        restart = False
        t0 = time.time()
        fadeout = self.truescreen.copy()
        fadeout.fill(constants.RED)
        messageSurface, messageRect, OHsurface, OHrect = self.render_gameover_message()
        while not restart:
            self.clock.tick(60)
            dead_time = time.time() - t0
            restart = self.gameover_events(t0, restart, dead_time)
            self.truescreen.fill(constants.LIGHT_BLUE)
            self.allSprites.draw(self.truescreen)
            self.draw_bomb_icons()
            fadeAlpha = int(dead_time*20)
            if fadeAlpha > 100:
                fadeAlpha = 100
            fadeout.set_alpha(fadeAlpha)
            self.truescreen.blit(fadeout, (0, 0))
            self.screen.blit(pg.transform.scale(self.truescreen, (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)), (0, 0))
            self.draw_score()
            if dead_time > 1:
                if int(dead_time*2)%2 == 0:
                    self.screen.blit(messageSurface, messageRect)
                self.screen.blit(OHsurface, OHrect)
            pg.display.flip()

        for sprite in self.allSprites:
            sprite.kill()

    def render_gameover_message(self):

        GOmessage = "Press any key to restart"
        messageSurface = self.font.render(GOmessage, True, constants.BLACK)
        messageRect = messageSurface.get_rect()
        messageRect.x = constants.WINDOW_WIDTH // 2 - 150
        messageRect.y = 750

        OHsurface = None
        OHrect = None
        new_high, oldscore = self.update_highscore()
        if new_high:
            OHmessage = "New highscore! Previous: {}".format(oldscore)
            OHsurface = self.font.render(OHmessage, True, constants.GREEN)
            OHrect = OHsurface.get_rect()
            OHrect.x = constants.WINDOW_WIDTH // 2 - OHrect.width//2
            OHrect.y = 350
        else:
            OHmessage = "Score to beat: {}".format(oldscore)
            OHsurface = self.font.render(OHmessage, True, constants.GREEN)
            OHrect = OHsurface.get_rect()
            OHrect.x = constants.WINDOW_WIDTH // 2 - OHrect.width//2
            OHrect.y = 350
            
        return messageSurface, messageRect, OHsurface, OHrect
                   

    def gameover_events(self, t0, restart, dead_time):

        self.deadFox.update()

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == KEYDOWN and dead_time > 2:
                restart = True
        return restart

    def update_highscore(self):
        highscore = 0.0
        new_highscore = False
        try:
            with open('highscore.txt', 'r') as f:
                l = f.readlines()
                highscore = int(l[0].strip())
        except OSError:
            pass
            
        with open('highscore.txt', 'w') as f:
            if highscore < self.score:
                f.write(str(self.score))
                new_highscore = True
            else:
                f.write(str(highscore))

        return (new_highscore, str(highscore))

    def draw_score(self):
        scoremessage = "Score: {}".format(self.score)
        scoreSurface = self.font.render(scoremessage, True, constants.GREEN)
        scoreRect = scoreSurface.get_rect()
        scoreRect.x = constants.WINDOW_WIDTH - 160
        scoreRect.y = 10
        self.screen.blit(scoreSurface, scoreRect)

    def load_icons(self):
        bomb_icon_filename = os.path.join('resources','images','bomb_icon.png')
        book = {}
        book['bomb_icon'] = pg.image.load(bomb_icon_filename).convert()
        book['bomb_icon'].set_colorkey(constants.WHITE)
        pale_bomb_icon_filename = os.path.join('resources','images','pale_bomb_icon.png')
        book['pale_bomb_icon'] = pg.image.load(pale_bomb_icon_filename).convert()
        book['pale_bomb_icon'].set_colorkey(constants.WHITE)
        bomb_upgrade_filename = os.path.join('resources','images','bomb_upgrade.png')
        book['bomb_upgrade'] = pg.image.load(bomb_upgrade_filename).convert()
        book['bomb_upgrade'].set_colorkey(constants.WHITE)
        return book

    def draw_bomb_icons(self):
        if self.maxbombs > self.bombs:
            for ghost_bomb in range(self.maxbombs):
                self.truescreen.blit(self.guibook['pale_bomb_icon'], (5+16*ghost_bomb, 8))
            partial_bomb_amount = self.bombs-int(self.bombs)
            partial_bomb_width = int(partial_bomb_amount * self.guibook['bomb_icon'].get_width())
            partial_bomb_height = self.guibook['bomb_icon'].get_height()
            partial_bomb = self.guibook['bomb_icon'].copy()
            partial_bomb.fill(constants.WHITE)
            partial_bomb.blit(self.guibook['bomb_icon'], (0, 0), area=Rect(0, 0, partial_bomb_width, partial_bomb_height))
            self.truescreen.blit(partial_bomb, (5+16*int(self.bombs), 8))
            
        for bomb in range(int(self.bombs)):
            self.truescreen.blit(self.guibook['bomb_icon'], (5+16*bomb, 8))


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

        if yPos > 300:
            if randint(1,1000) > 900 - self.luck:
                butt = Butterfly(self, randint(0,200), yPos)
                self.allSprites.add(butt, layer=2)
                self.butterflies.append(butt)

    def load_starting_section(self):
        self.load_section_into_rows("start")

    def load_new_section(self):
        
        oldrowsLoaded = len(self.rows)
        sectionsToLoad = len(os.listdir(os.path.join('resources', 'images', 'sections'))) - 1
        sectionNumber = randint(1,sectionsToLoad)
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
        if randint(1,1000) > 990 - self.scrollLength/30 + self.luck:
            spike = Spike(self, x, y, direction)
            self.allSprites.add(spike, layer=-1)
            self.spikes.append(spike)

def main():
    game = Game()
    while True:
        game.start()

main()
