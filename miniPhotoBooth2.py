#!/usr/bin/python
from PIL import Image
import io
import os
import picamera
import time
import RPi.GPIO as GPIO
import pygame
from pygame.locals import *
import sys
import cups
import syslog

#Prerequisites:
# find out what version of python your raspberry pi uses by typing 'python --version' on the command line
# install PILLOW (the replacement for PIL, aka Python Image Library) by googling 'install pillow python ###' where ### is your python version

#general setup things here
syslog.syslog('Starting Photobooth')
os.system("amixer cset numid=3 1")
xPhotoResolution = 800 #screen resolution, not photo resolution
yPhotoResolution = 480

try:
    camera = picamera.PiCamera()
    camera.resolution = (1120, 750)
    camera.vflip = True
    camera.hflip = False
    syslog.syslog('start preview')
    camera.start_preview()
    camera.preview.fullscreen = True
    camera.preview_alpha = 100
except Exception:
    syslog.syslog('Error in camera setup')
    sys.exit()


try:
    pygame.init()
    window = pygame.display.set_mode((xPhotoResolution, yPhotoResolution)) ##This is the 'base' layer that will get all the updates and redraws - this is a global variable.
    pygame.display.set_caption('Chase and Abby!') #does not actually do anything unless you have a titlebar...
    background = pygame.Surface(window.get_size()) #when you want to make a change, make a new 'surface', we called our surface variable 'background' for this round.
    background.fill((0, 0, 0)) # do something to the surface, like filling it. note the double parentheses, I think they are important
    font = pygame.font.Font(None, 700)
    messageFont = pygame.font.Font(None, 200)
    countFont = pygame.font.Font(None, 80) #make a font object
except Exception:
    syslog.syslog('Error in pygame setup')
    sys.exit()


# Methods Start here:
def timestamp():
    return format('%s-%s %s:%s:%s') % (
    time.localtime()[1], time.localtime()[2], time.localtime()[3], time.localtime()[4], time.localtime()[5])


# Pygame Counter
def startCountdown(photoCount):
    try:
        syslog.syslog('starting countdown')
        countDown = 5

        while countDown > 0:
            if (countDown == 1):
                message = ':)'
            else:
                message = countDown - 1
            background = pygame.Surface(window.get_size()) #fun example 2: make a surface and call it something memorable
            text = font.render(str(message), 1, (255, 255, 255)) #rendering font (see line #44 where I initalized this variable with the 'string' of my message variable, 1, and the color white, see https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render
            photosRemain = '%s / 4' % (photoCount)
            photoCountbox = countFont.render(str(photosRemain), 1, (0, 255, 0))
            msgRectObj = photoCountbox.get_rect() #get size of our rendering
            msgRectObj.topleft = (10, 20) #set the topleft corner to start at x=10, y=20 pixels... forgetting why I put this here, actually
            xPos = (xPhotoResolution // 2) - (text.get_width() // 2) #get the center start for x
            yPos = (yPhotoResolution // 2) - (text.get_height() // 2)#get the center start for y
            background.blit(text, (xPos, yPos)) #BLIT is Block level image transfer. use .blit to put one image ontop of another, and blit your final image onto window and .flip() to update. see https://www.pygame.org/docs/ref/surface.html#pygame.Surface.blit
            background.blit(photoCountbox, msgRectObj) #here we are putting the msgRectObject onto the source image of 'photoCountBox', from the docs: 'Dest can either be pair of coordinates representing the upper left corner of the source. A Rect can also be passed as the destination and the topleft corner of the rectangle will be used as the position for the blit. The size of the destination rectangle does not effect the blit.' I guess that explains why I did the .topleft assignment earlier
            window.blit(background, (0, 0)) #put our background image onto the window surface
            pygame.display.flip() #tell pygame to update
            if countDown == 1:
                return
            else:
                time.sleep(1.5)
                countDown = countDown - 1
    except:
        syslog.syslog('error in startCountdown')


def compileMessage():
    try:
        message = 'Please wait'
        background = pygame.Surface(window.get_size())
        text = messageFont.render(str(message), 1, (255, 255, 255))
        xPos = (xPhotoResolution // 2) - (text.get_width() // 2)
        yPos = (yPhotoResolution // 2) - (text.get_height() // 2)
        background.blit(text, (xPos, yPos))
        window.blit(background, (0, 0))
        pygame.display.flip()
    except:
        syslog.syslog('error in compileMessage')


def blackScreen():
    try:
        syslog.syslog('blanking out screen')
        img = pygame.image.load('touchtesttrans.tif') #fun example 3: blitting an image onto the window - make certain the image is the right size or pygame complains and crashes out.
        background2 = pygame.Surface(window.get_size()) #get a new surface the size of the window
        background2.fill((0, 0, 0)) #optional: background fille
        background2.blit(img, (0, 0)) #place image starting at 0,0)
        window.blit(background2, (0, 0)) #place background onto window
        pygame.display.flip() #tell pygame to update.
        syslog.syslog('flipped')
    except Exception:
        syslog.syslog('blackScreen errored')


def buttonPressed():
    try:
        syslog.syslog('button pressed!')
        now = time.time()
        counter = 4
        photoTaken = 1

        while counter > 0:
            # Countdown timer, etc.
            startCountdown(photoTaken)
            # capture photo
            filename = 'img%s.jpg' % (counter)
            start = time.time()
            camera.capture(filename, use_video_port=True)
            os.system("aplay -f S24_LE camera-shutter-click-03.wav")
            syslog.syslog('Capture took ' + str('%.2fs' % (time.time() - start)))
            counter = counter - 1
            photoTaken = photoTaken + 1

        compileMessage()
        tile_images_wrapper()
        print('done with button press, %s sec' % (time.time() - now))
    except Exception:
        syslog.syslog('error in buttonPressed')


def tile_images_wrapper():
    try:
        syslog.syslog('launching thinger that does the montage')
        now = time.time()
        manually_arrange()
        syslog.syslog('Montage thing done! ' + str('%s' % (time.time() - now)))
    except Exception:
        syslog.syslog('error in tile_images_wrapper')


def manually_arrange():
    try:
        syslog.syslog('inside manually arrange') #fun example 4: arranging 4x smaller photos into a larger photo strip!
        isize = (1200, 3600) #this is the final size in pixels of the strip!
        first = (40, 40, 1160, 790) #this is the rectangle that is the first photo
        second = (40, 830, 1160, 1580)
        third = (40, 1620, 1160, 2370)
        fourth = (40, 2409, 1160, 3159)
        label = (40, 3199, 1160, 3560) #this is the label
        white = (255, 255, 255)
        inew = Image.new('RGB', isize, white) #using Python Image Library fork (PILLOW)
        syslog.syslog('open img4')
        img4time = time.time()
        img = Image.open('img4.jpg')
        inew.paste(img, first) #if the image you open does not fit exactly into the same pixel size, python complains and crashes.
        syslog.syslog('pasted img4 in' + str('%.2fs' % (time.time() - img4time)))
        # print('pasted') #ignore timing and diagnostic information.
        img3time = time.time()
        img = Image.open('img3.jpg')
        inew.paste(img, second)
        syslog.syslog('pasted img3 in' + str('%.2fs' % (time.time() - img3time)))
        # print('pasted')
        img2time = time.time()
        img = Image.open('img2.jpg')
        inew.paste(img, third)
        syslog.syslog('pasted img2 in' + str('%.2fs' % (time.time() - img2time)))
        # print('pasted')
        img1time = time.time()
        img = Image.open('img1.jpg')
        inew.paste(img, fourth)
        syslog.syslog('pasted img1 in' + str('%.2fs' % (time.time() - img1time)))
        # print('pasted')
        imgLabeltime = time.time()
        # img = Image.open('photobooth-04.png')
        # img = Image.open('photoboothwedding.png')
        # img = Image.open('photoboothhalloween.png')
        # img = Image.open('SBHoliday2017-01.png')
        syslog.syslog('attempting open banner')
        img = Image.open('GreganPhotobooth-02.png')
        syslog.syslog('opened photo, attempting paste label')
        inew.paste(img, label)
        syslog.syslog('Pasted Label' + str('%.2fs' % (time.time() - imgLabeltime)))
        start = time.time()
        fileName = './archive/%s.tiff' % (timestamp())
        inew.save(fileName) #save the file
        syslog.syslog('Save took ' + str('%.2fs' % (time.time() - start)))
        start = time.time()
        # job_id = conn.printFile('EPSON_PictureMate_PM_225', fileName, 'test',{}) #CUPS is common unix print server. this sends the photo there and gets a jobid in return. if you're not using CUPS, comment this out, because I try to log the ID of it in a silly way.
        # syslog.syslog('job_id: '+ str(job_id))
        syslog.syslog('Send took ' + str('%.2fs' % (time.time() - start)))
    except:
        syslog.syslog('error in manual arrange')
        pass

#Actual important looping stuff starts here.
syslog.syslog('starting loop?')
blackScreen() #set up the base 'touch here to start' screen
# MAIN
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP: #for the touchscreen we use, it registers a touch as a mouse click, we want to do something when they take their finger off the screen
            buttonPressed() #do the things
            blackScreen() #reset the screen to blank background with 'touch here to start' message
        elif event.type == KEYDOWN: #if there's a keyboard attached, any keypress will exit. might want to configure this differently?
            pygame.quit()
            sys.exit()
