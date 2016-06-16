import pygame, sys
import random
from gameObjects import *

pygame.init()
#pygame.mixer.Sound("../audio/sound.mp3")
#sound.play()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 600))

gameObjs = []

background = Background("images/Nebula1.bmp",
                        screen.get_width(), screen.get_height())

player = Player("images/Hunter1.bmp",2, (25, 1, 23, 23))
playerRotate = pygame.transform.rotate(player.image, 30)
gameObjs.append(player)

waveManager = WaveManager()
enemies = []
for i in range(3):
    enemy = Enemy("images/SpacStor.bmp",
                  1,
                  (101, 13, 91, 59),
                  (screen.get_width() + 91, screen.get_height()+ 59),
                  player,
                  waveManager )
    enemies.append(enemy)
    gameObjs.append(enemy)
    player.collisionGroup.append(enemy)

asteroids = []
for i in range(3):
    asteroid = Asteroid("images/Rock2a.bmp",
                        1,
                        (6, 3, 80, 67),
                        (screen.get_width() + 80, screen.get_height() + 67) )
    asteroids.append(asteroid)
    gameObjs.append(asteroid)
#    player.collisionGroup.append(asteroid)

scoreBoardFrames = []
numbersWidth = 26
for i in range(0, 10):
    scoreBoardFrames.append(
        imageLoader("images/num.png",
        1,
        (numbersWidth * i, 0, 26,36)
    ))
    scoreBoardFrames[i].set_colorkey( (0,0,0) )

while True:

    for event in pygame.event.get():
        if event.type== pygame.QUIT:
            sys.exit()

    # update wave
    waveManager.update()

    # update object
    for g in gameObjs:
        g.update()

    # render
    if player.collision:
        screen.fill((255,0,0))
    else:
        screen.blit(background.image, (0,0))
    for g in gameObjs:
        screen.blit(g.image, (g.rect.x, g.rect.y))

    # Render score
    FirstDigit = waveManager.score % 10
    secondDigit = waveManager.score % 100 - FirstDigit
    thirdDigit = waveManager.score % 1000 - FirstDigit - secondDigit
    screen.blit(scoreBoardFrames[FirstDigit], (64, 0))
    screen.blit(scoreBoardFrames[secondDigit/10], (32, 0) )
    screen.blit(scoreBoardFrames[thirdDigit/100], (0,0))
    # Render wave
    FirstDigit = waveManager.currentWave % 10
    secondDigit = waveManager.currentWave % 100 - FirstDigit
    thirdDigit = waveManager.currentWave % 1000 - FirstDigit - secondDigit
    waveNumberWidth = screen.get_width() - 26
    screen.blit(scoreBoardFrames[FirstDigit], (waveNumberWidth, 0))
    screen.blit(scoreBoardFrames[secondDigit/10], (waveNumberWidth-32, 0) )
    screen.blit(scoreBoardFrames[thirdDigit/100], (waveNumberWidth-64,0))
    pygame.display.flip()

    # test
    clock.tick(60)
