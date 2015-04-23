import pygame, sys,os, random, pygame.gfxdraw, math
from pygame.locals import *
import numpy  # sudo apt-get install python-numpy
import pdb # debugger
import time
import csv

# Annotate images
# Andy Barry
# Dec 2014

# defaults

IMAGE_START = 1 #694


IMAGE_DIR = '/Users/pflomac/Desktop/Hack/ProjectWind/simple-image-annotation/images/'
image_number = IMAGE_START


def LoadImage(image_number):

    filepath = IMAGE_DIR + "frame-%d.tif" % image_number

    img = pygame.image.load(filepath)

    return img

def DrawLabel(img, image_number):
    # draw the frame number onto the image
    myfont = pygame.font.SysFont("monospace", 15) # Font for image label
    textfont = pygame.Color(0, 0, 0)  # black
    backgroundfont = pygame.Color(255, 255, 255) # white
    label = myfont.render(str(image_number), True, textfont, backgroundfont) # What does the second argument do?

    img.blit(label, (25, 25)) # Position of the image label in the frame (currently NorthWest)

    return img

class AnnotationBox(pygame.sprite.Sprite):

    def __init__(self, pos):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([100, 100], SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color(128, 128, 128), self.image.get_rect(), 3)

        self.image.convert_alpha()

        self.rect = self.image.get_rect()

        self.click_x = pos[0]
        self.click_y = pos[1]

        self.ResizeBox(pos)

        self.visible = True

    def update(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height], pygame.SRCALPHA)
        self.image.fill(pygame.Color(128, 128, 128, 128))

    def ResizeBox(self, pos):

        if self.click_x < pos[0]:

            self.rect.width = pos[0] - self.click_x

        else:
            self.rect.left = pos[0]
            self.rect.width = self.click_x - pos[0]

        if self.click_y < pos[1]:

            self.rect.height = pos[1] - self.click_y

        else:
            self.rect.top = pos[1]
            self.rect.height = self.click_y - pos[1]


    def ProcessMouseMove(self, event):
        # resize the box as the mouse moves
        self.ResizeBox(event.pos)

    def ProcessClick(self, event):
        self.ResizeBox(event.pos)
        self.visible = False

    def PrintState(self):
        print str(self.rect.left) + ', ' + str(self.rect.top) + ', ' + str(self.rect.right) + ', ' + str(self.rect.bottom)


# this class holds multiple boxes so that we can define regions of the image
# with multiple boxes
class AnnotationBoxes():

    def __init__(self):
        self.ResetBoxes()


    def ResetBoxes(self):
        self.boxes = []
        self.number_of_clicks = 0

    def ProcessClick(self, event):

        if self.number_of_clicks % 2 == 0:
            # create a new box
            self.boxes.append(AnnotationBox(event.pos))

        else:

            # continue a box
            self.boxes[-1].ProcessClick(event)

        self.number_of_clicks = self.number_of_clicks + 1

    def ProcessMouseMove(self, event):
        if self.number_of_clicks % 2 == 0:
            # waiting for a new box
            pass
        else:
            self.boxes[-1].ProcessMouseMove(event)


    def Finish(self, image_number):

        # print out all box data

        for box in self.boxes:
            sys.stdout.write(str(image_number) + ', ')
            box.PrintState()

        sys.stdout.flush()

        self.ResetBoxes()

    def AddAllSprites(self, allsprites):
        for box in self.boxes:
            allsprites.add(box)

        return allsprites



BG_COLOR = pygame.Color(255, 255, 255)

pygame.init()

img = LoadImage(image_number)

window = pygame.display.set_mode((img.get_rect().width, img.get_rect().height))

pygame.display.set_caption('Image Annotation')

img = DrawLabel(img, image_number)

screen = pygame.display.get_surface()

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250)) # Where does background fill show up?

screen.blit(background, (0, 0))
pygame.display.flip()

clock = pygame.time.Clock()

boxes = AnnotationBoxes()

pygame.key.set_repeat(50)

print 'image_number, left, top, right, bottom' #label for the positions of the boxes to be drawn

while True:
    #input(pygame.event.get())

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        
        # Keyboard interactions
        elif event.type == KEYDOWN:  # If a button is pressed
            if event.key == K_ESCAPE or event.key == 113: # Can press Esc or Q at any time to quit (113 = q)
                exit()
            elif event.key == K_RIGHT: # Can press right arrow to move to next image
                # skip this image
                image_number = image_number + 1
                img = LoadImage(image_number)
                img = DrawLabel(img, image_number)
                boxes.ResetBoxes()

            elif event.key == K_LEFT: # Can press left arrow to move to previous image
                image_number = image_number - 1
                img = LoadImage(image_number)
                img = DrawLabel(img, image_number)
                boxes.ResetBoxes()

        # Mouse interactions
        elif event.type == MOUSEBUTTONUP:
            
            if event.button == 1: # Left click to draw
                boxes.ProcessClick(event)

            elif event.button == 3: # Right click to print box locations, and move to next image

                    boxes.Finish(image_number)

                    # load a new image
                    image_number = image_number + 1
                    img = LoadImage(image_number)
                    img = DrawLabel(img, image_number)

        elif event.type == MOUSEMOTION:
            boxes.ProcessMouseMove(event)



    background.fill(BG_COLOR)



    screen.blit(background, (0, 0))
    screen.blit(img, img.get_rect())

    allsprites = pygame.sprite.Group()
    allsprites = boxes.AddAllSprites(allsprites)
    allsprites.update()

    allsprites.draw(screen)

    pygame.display.flip()
    clock.tick(60) #What does the clock tick do?


