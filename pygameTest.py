import pygame
import time

pygame.init()

window = pygame.display.set_mode((1920,1200))
pygame.display.set_caption('Example PhotBooth')

background = pygame.Surface(window.get_size())
background.fill((0,0,0))

font = pygame.font.Font(None, 1000)
counter = 3

while counter > 0:
 background = pygame.Surface(window.get_size())
 text = font.render(str(counter), 1, (255,0,0))
 xpos = 960 - (text.get_width()//2)
 ypos = 600 - (text.get_height()//2)

 background.blit(text, (xpos,ypos))
 window.blit(background, (0,0))
 pygame.display.flip()
 counter = counter -1  
 time.sleep(1)
 pygame.display.flip()

pygame.quit()
print('quit')

