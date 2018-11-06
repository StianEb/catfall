#from classes import Spritesheet
from os import path

GRAVITY = 0.35

WINDOW_WIDTH = 420
WINDOW_HEIGHT = 600

PURPLE = (148, 0, 211)
LIGHT_BLUE = (80,80,255)
PLAYER_BG = (31, 223, 150)

HOME_DIR = path.dirname(path.realpath(__file__))
IMAGES_DIR = HOME_DIR + "\\resources\\images"
#spritesheet = Spritesheet(IMAGES_DIR + "\\player.png")
#PLAYER_STANDING = [spritesheet.get_image(86, 439, 16, 24).set_colorkey(PLAYER_BG)]
