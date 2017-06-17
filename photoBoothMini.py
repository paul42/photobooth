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

syslog.syslog('Starting Photobooth')

#force audio out headphone jack
os.system("amixer cset numid=3 1")

# x and y Resolution of photo 
xPhotoResolution = 800
#xPhotoResolution = 1120
#xPhotoResolution = 1120
yPhotoResolution = 480
#yPhotoResolution = 750
#yPhotoResolution = 750

#Camera Setup
camera = picamera.PiCamera()
camera.resolution = (1120,750)
camera.vflip = True
camera.hflip = False

#Pin setup
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(17,GPIO.IN)
#GPIO.setup(22,GPIO.OUT)
#GPIO.output(22,1)
#input = GPIO.input(17)
#prev_input = 1
#counter = 0

#Camera Start
syslog.syslog('start preview')
camera.start_preview()
camera.preview.fullscreen = True 
camera.preview_alpha = 100

#Printer init
syslog.syslog('start cups connection')
conn = cups.Connection()
conn.enablePrinter('EPSON_PictureMate_PM_225')
syslog.syslog('enable printer')
#counter init here, because, whatever.
counter = 4 

#pygame Setup
pygame.init()
window = pygame.display.set_mode((xPhotoResolution, yPhotoResolution))
pygame.display.set_caption('Chase and Abby!')
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
 syslog.syslog('starting countdown')
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
  if countDown == 1:
      return
  else:
      time.sleep(1.5)
      countDown = countDown -1

def compileMessage():
  message = 'Please wait'
  background = pygame.Surface(window.get_size())
  text = messageFont.render(str(message),1,(255,255,255))
  xPos = (xPhotoResolution // 2 ) - (text.get_width()//2)
  yPos = (yPhotoResolution // 2 ) - (text.get_height()//2)
  background.blit(text, (xPos,yPos))
  window.blit(background, (0,0))
  pygame.display.flip()

def blackScreen():
  syslog.syslog('blanking out screen')
  img = pygame.image.load('touchtesttrans.tif')
  background2 = pygame.Surface(window.get_size())
  background2.fill((0,0,0))
  background2.blit(img, (0,0))
  window.blit(background2,(0,0))
  pygame.display.flip()
  #message = 'Touch to Start'
  #text = messageFont.render(str(message),1,(255,255,255))
  #xPos = (xPhotoResolution // 2 ) - (text.get_width()//2)
  #yPos = (yPhotoResolution // 2 ) - (text.get_height()//2)
  #background.blit(text, (xPos,yPos))
  #window.blit(background, (0,0))
  #pygame.display.flip()

def buttonPressed():
  syslog.syslog('button pressed!')
  now = time.time()
  counter = 4 
  photoTaken = 1
  
  while counter > 0:
    #Countdown timer, etc.
    startCountdown(photoTaken)
    #capture photo 
    filename = 'img%s.jpg' % (counter)
    start = time.time()
    camera.capture(filename, use_video_port=True)
    os.system("aplay -f S24_LE camera-shutter-click-03.wav")
    syslog.syslog('Capture took '+ str('%.2fs' % (time.time()-start)))
    counter = counter - 1
    photoTaken = photoTaken +1
  
  compileMessage()
  tile_images_wrapper()
  print('done with button press, %s sec'%(time.time()-now))

def tile_images_wrapper():
  syslog.syslog('launching thinger that does the montage')
  now = time.time()
  manually_arrange()
  syslog.syslog('Montage thing done! '+str('%s'%(time.time()-now)))

def manually_arrange():
  syslog.syslog('inside manually arrange')
  isize = (1200,3600)
  first = (40,40,1160,790) 
  second = (40,830,1160,1580)
  third = (40,1620,1160,2370)
  fourth = (40,2409,1160,3159)
  label = (40,3199,1160,3560)
  white = (255,255,255)
  inew = Image.new('RGB',isize,white)
  syslog.syslog('open img4')
  img4time = time.time()
  img = Image.open('img4.jpg')
  inew.paste(img,first)
  syslog.syslog('pasted img4 in' +str('%.2fs'% (time.time()-img4time)))
  #print('pasted')
  img3time = time.time()
  img = Image.open('img3.jpg')
  inew.paste(img,second)
  syslog.syslog('pasted img3 in' +str('%.2fs'% (time.time()-img3time)))
  #print('pasted')
  img2time = time.time()
  img = Image.open('img2.jpg')
  inew.paste(img,third)
  syslog.syslog('pasted img2 in' +str('%.2fs'% (time.time()-img2time)))
  #print('pasted')
  img1time = time.time()
  img = Image.open('img1.jpg')
  inew.paste(img,fourth)
  syslog.syslog('pasted img1 in' +str('%.2fs'% (time.time()-img1time)))
  #print('pasted')
  imgLabeltime = time.time()
  #img = Image.open('photobooth-04.png')
  #img = Image.open('photoboothwedding.png')
  #img = Image.open('photoboothhalloween.png')
  #img = Image.open('SBHoliday2017-01.png')
  syslog.syslog('attempting open banner')
  img = Image.open('GreganPhotobooth-02.png')
  syslog.syslog('opened photo, attempting paste label')
  inew.paste(img,label)
  syslog.syslog('Pasted Label'+str('%.2fs' %(time.time()-imgLabeltime)))
  start = time.time()
  fileName = './archive/%s.tiff' % (timestamp())
  inew.save(fileName)
  syslog.syslog('Save took '+str('%.2fs' % (time.time()-start)))
  start = time.time()
  #job_id = conn.printFile('EPSON_PictureMate_PM_225', fileName, 'test',{})
  #syslog.syslog('job_id: '+ str(job_id))
  syslog.syslog('Send took '+ str('%.2fs' % (time.time()-start)))
  


syslog.syslog('starting loop?')
blackScreen()
#MAIN
while True:
 for event in pygame.event.get():
   if event.type == QUIT:
     pygame.quit()
     sys.exit()
   elif event.type == pygame.MOUSEBUTTONUP:
    buttonPressed()
    blackScreen()
   elif event.type == KEYDOWN:
     if event.key == K_ESCAPE:
       pygame.quit()
       sys.exit()
