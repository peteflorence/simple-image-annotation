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

IMAGE_START = 200 
IMAGE_END   = 450


IMAGE_DIR = '/Users/pflomacpro/ProjectWind/ImageProcessing/out_imagefolder/'
image_number = IMAGE_START

displayallsprites = False


def LoadImage(image_number):

    filepath = IMAGE_DIR + "UDvideoframe%d.bmp" % image_number

    img = pygame.image.load(filepath)

    return img

def DrawLabel(img, image_number):
    # draw the frame number onto the image
    myfont = pygame.font.SysFont("monospace", 15) # Font for image label
    textfontcolor = pygame.Color(0, 0, 0)  # black
    backgroundfontcolor = pygame.Color(255, 255, 255) # white
    label = myfont.render(str(image_number), True, textfontcolor, backgroundfontcolor) # What does the second argument do?

    img.blit(label, (25, 25)) # Position of the image label in the frame (currently NorthWest)

    return img

class AnnotationLine(pygame.sprite.Sprite):

    def __init__(self, pos):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([100, 100], SRCALPHA)
        pygame.draw.rect(self.image, pygame.Color(128, 0, 0, 128), self.image.get_rect(), 3)

        self.image.convert_alpha()

        self.rect = self.image.get_rect()

        self.click_x = pos[0]
        self.click_y = pos[1]

        self.ResizeLine(pos)

        self.visible = True
        self.imgnumber = image_number

    def update(self):
        self.image = pygame.Surface([self.rect.width, self.rect.height], pygame.SRCALPHA)
        self.image.fill(pygame.Color(128, 0, 0, 128))

    def ResizeLine(self, pos):

        ## These two lines to draw vertical line
        self.rect.left = self.click_x - 3
        self.rect.width = 6

        ## These next six lines to draw a box
        #if self.click_x < pos[0]:
        #
        #    self.rect.width = pos[0] - self.click_x
        #else:
        #    self.rect.left = pos[0]
        #    self.rect.width = self.click_x - pos[0]

        if self.click_y < pos[1]:

            self.rect.height = pos[1] - self.click_y

        else:
            self.rect.top = pos[1]
            self.rect.height = self.click_y - pos[1]


    def ProcessMouseMove(self, event):
        # resize the lin as the mouse moves
        self.ResizeLine(event.pos)

    def ProcessClick(self, event):
        self.ResizeLine(event.pos)
        self.visible = False

    def PrintState(self):
        print str(self.rect.left) + ', ' + str(self.rect.top) + ', ' + str(self.rect.right) + ', ' + str(self.rect.bottom)


# this class holds multiple lines so that we can define regions of the image
# with multiple lines
class AnnotationLines():

    def __init__(self):
        self.InitLines()

    def InitLines(self):
        self.lines = []
        self.number_of_clicks = 0    

    def ResetLines(self):
        #print(self.lines)
        self.number_of_clicks = 0

    def ProcessClick(self, event):

        if self.number_of_clicks % 2 == 0:
            
            for i in range(len(self.lines)):
                line = self.lines[i]
                if line.imgnumber == image_number:
                    print('Already have a box for this img')
                    #self.lines.pop(i)
                    #self.lines.insert(i,AnnotationLine(event.pos))
                    self.lines[i] = AnnotationLine(event.pos)
                    break
            # create a new line
            else: 
                print('Now Im creating a new box')
                self.lines.append(AnnotationLine(event.pos))

        else:
            for i in range(len(self.lines)):
                line = self.lines[i]
                if line.imgnumber == image_number:
                    line.ProcessClick(event)
                    break

        self.number_of_clicks = self.number_of_clicks + 1

    def ProcessMouseMove(self, event):
        if self.number_of_clicks % 2 == 0:
            # waiting for a new lin
            pass
        else:
            for i in range(len(self.lines)):
                line = self.lines[i]
                if line.imgnumber == image_number:
                    line.ProcessClick(event)
                    break


    def Finish(self, image_number):

        # print out all line data

        for line in self.lines:
            sys.stdout.write(str(line.imgnumber) + ', ')
            line.PrintState()

        sys.stdout.flush()

        self.ResetLines()

    def AddCurrentSprites(self, allsprites, image_number):
        for line in self.lines:
            if line.imgnumber == image_number:
                allsprites.add(line)

        return allsprites

    def AddAllSprites(self, allsprites):
        for line in self.lines:
            allsprites.add(line)

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

lines = AnnotationLines()

pygame.key.set_repeat(50)

print 'image_number, left, top, right, bottom' #label for the positions of the lines to be drawn

while True:
    #input(pygame.event.get())

    if image_number == IMAGE_END:
        exit()

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
                lines.ResetLines()

            elif event.key == K_LEFT: # Can press left arrow to move to previous image
                image_number = image_number - 1
                img = LoadImage(image_number)
                img = DrawLabel(img, image_number)
                lines.ResetLines()

            elif event.key == K_SPACE:
                displayallsprites = not(displayallsprites)

        # Mouse interactions
        elif event.type == MOUSEBUTTONUP:
            
            if event.button == 1: # Left click to draw
                lines.ProcessClick(event)

            elif event.button == 3: # Right click to print lin locations, and move to next image

                    lines.Finish(image_number)

                    # load a new image
                    image_number = image_number + 1
                    img = LoadImage(image_number)
                    img = DrawLabel(img, image_number)

        elif event.type == MOUSEMOTION:
            lines.ProcessMouseMove(event)

        



    background.fill(BG_COLOR)



    screen.blit(background, (0, 0))
    screen.blit(img, img.get_rect())

    allsprites = pygame.sprite.Group()
    if displayallsprites:
        allsprites = lines.AddAllSprites(allsprites)
    else:
        allsprites = lines.AddCurrentSprites(allsprites,image_number)
    allsprites.update()

    allsprites.draw(screen)

    pygame.display.flip()
    clock.tick(60) #What does the clock tick do?


