import picamera
import time
import RPi.GPIO as GPIO

def timestamp():
 return format('%s-%s %s:%s:%s') % (time.localtime()[1],time.localtime()[2],time.localtime()[3],time.localtime()[4],time.localtime()[5])

camera = picamera.PiCamera()

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)
input = GPIO.input(17)

prev_input = 1
counter = 0
camera.preview_alpha = 128

camera.start_preview()

def buttonPressed():
  filename = 'img%s.jpg' % (timestamp())
  camera.capture(filename)
  camera.stop_preview()
  time.sleep(1)
  camera.start_preview()


while True:
 input = GPIO.input(17)
 if ((not prev_input) and input):
  buttonPressed()
 prev_input = input
 time.sleep(0.05)



