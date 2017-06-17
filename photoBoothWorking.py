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
import threading

# x and y Resolution of photo 
xPhotoResolution = 1120
yPhotoResolution = 750

#Camera Setup
camera = picamera.PiCamera()
camera.resolution = (xPhotoResolution,yPhotoResolution)
camera.vflip = True
camera.hflip = True

#Pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)
GPIO.setup(22,GPIO.OUT)
GPIO.output(22,1)
input = GPIO.input(17)
prev_input = 1
counter = 0

#Camera Start
camera.start_preview()
camera.preview.fullscreen = True 
camera.preview_alpha = 100

#Printer init
conn = cups.Connection()

#counter init here, because, whatever.
counter = 4 

#pygame Setup
pygame.mixer.pre_init(44100,-16,2,2048)
pygame.init()
pygame.mixer.music.load('shutter.mp3')
fpsClock = pygame.time.Clock()
window = pygame.display.set_mode((xPhotoResolution, yPhotoResolution))
pygame.display.set_caption('Paul and Jess 11.15.2014!')
background = pygame.Surface(window.get_size())
background.fill((0,0,0))
font = pygame.font.Font(None,700)
messageFont = pygame.font.Font(None,200)
countFont = pygame.font.Font(None,80)

#Methods Start here:
def timestamp():
 return format('%s-%s %s:%s:%s') % (time.localtime()[1],time.localtime()[2],time.localtime()[3],time.localtime()[4],time.localtime()[5])


#Pygame Counter
def startCountdown(photoCount):
 countDown = 5
 
 while countDown > 0:
  if(countDown == 1):
    message = ':)'
  else:
    message = countDown -1 
  background = pygame.Surface(window.get_size())
  text = font.render(str(message),1,(255,255,255))
  photosRemain = '%s / 4' % (photoCount)
  photoCountbox = countFont.render(str(photosRemain),1,(0,255,0))
  msgRectObj = photoCountbox.get_rect()
  msgRectObj.topleft = (10,20)
  xPos = (xPhotoResolution // 2 ) - (text.get_width()//2)
  yPos = (yPhotoResolution // 2 ) - (text.get_height()//2)
  background.blit(text, (xPos,yPos))
  background.blit(photoCountbox, msgRectObj)
  window.blit(background, (0,0))
  pygame.display.flip()
  countDown = countDown -1
  time.sleep(1)



def compileMessage():
  message = 'Please wait...'
  background = pygame.Surface(window.get_size())
  text = messageFont.render(str(message),1,(255,255,255))
  xPos = (xPhotoResolution // 2 ) - (text.get_width()//2)
  yPos = (yPhotoResolution // 2 ) - (text.get_height()//2)
  background.blit(text, (xPos,yPos))
  window.blit(background, (0,0))
  pygame.display.flip()

def blackScreen():
  background = pygame.Surface(window.get_size())
  background.fill((0,0,0))
  window.blit(background,(0,0))
  pygame.display.flip()


def buttonPressed():
  print('button pressed!')
  now = time.time()
  counter = 4 
  photoTaken = 1
  
  while counter > 0:
    #stream = io.BytesIO()
    #Countdown timer, etc.
    startCountdown(photoTaken)
    #capture photo 
    filename = 'img%s.png' % (counter)
    start = time.time()
    camera.capture(filename, format='png', use_video_port=True)
    pygame.mixer.music.play()
    print('Capture took %.2fs' % (time.time()-start))
    #stream.seek(0)
    #photos.append(Image.open(stream))
    #stream.seek(0)
    #stream.truncate()
                  
    #pygame.mixer.music.play()
    print('picture taken! %s of 4') % photoTaken  
    counter = counter - 1
    photoTaken = photoTaken +1
  
  compileMessage()
  tile_images_wrapper()
  print('done with button press, %s sec'%(time.time()-now))

def tile_images_wrapper():
  print('launching thinger that does the montage')
  now = time.time()
  manually_arrange()
  print('Montage thing done! %s'%(time.time()-now))

def manually_arrange():
  #print('inside manually arrange')
  isize = (1200,3600)
  first = (40,40,1160,790) 
  second = (40,830,1160,1580)
  third = (40,1620,1160,2370)
  fourth = (40,2409,1160,3159)
  label = (40,3199,1160,3560)
  white = (255,255,255)
  inew = Image.new('RGB',isize,white)
  print('made new image')
  img = Image.open('img4.png')
  inew.paste(img,first)
  print('pasted')
  img = Image.open('img3.png')#.resize((560,375))
  inew.paste(img,second)
  print('pasted')
  img = Image.open('img2.png')#.resize((560,375))
  inew.paste(img,third)
  print('pasted')
  img = Image.open('img1.png')#.resize((560,375))
  inew.paste(img,fourth)
  print('pasted')
  img = Image.open('photoboothwedding.png')
  #img = Image.open('photoboothhalloween.png')
  inew.paste(img,label)
  print('pasted')
  start = time.time()
  fileName = './archive/%s.tiff' % (timestamp())
  inew.save(fileName)
  print('SAVE took %.2fs' % (time.time()-start))
  start = time.time()
  conn.printFile('EPSON_PictureMate_PM_225', fileName, 'test',{})
  print('Send took %.2fs' % (time.time()-start))


#MAIN
while True:
 for event in pygame.event.get():
   if event.type == QUIT:
     pygame.quit()
     sys.exit()
   elif event.type == KEYDOWN:
     if event.key == K_ESCAPE:
       pygame.quit()
       GPIO.output(22,0)
       sys.exit()
 input = GPIO.input(17)
 if ((not prev_input) and input):
  GPIO.output(22,0)
  buttonPressed()
 blackScreen()
 GPIO.output(22,1)
 prev_input = input
 time.sleep(0.05)

