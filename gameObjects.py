import pygame
import random
import math
from imageLoader import *

RespawnDelay = 120 # Ticks

class Background(pygame.sprite.Sprite):
    def __init__(self, image, width, height):
        self.origin = pygame.image.load(image)
        self.image = pygame.transform.scale(self.origin, (width, height))
        self.rect = self.image.get_rect()

    def update(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip):
        self.asset = imageLoader(image, scale, clip)
        self.image = self.asset
        self.planeColorKey = (0,0,0)
        self.explodeColorKey = 0x454e5b
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 300
        self.velocityX = 0
        self.velocityY = 0
        self.accelerationX = 0
        self.accelerationY = 0
        self.thrust = 0.5
        self.damping = 0.3
        self.angle = 0
        self.maxVelocity = 8
        self.collision = False
        self.collisionGroup = []
        self.isWaitingToRespawn = False
        self.waitingToRespawn = 0
        self.explosionCurrentFrame = 0
        self.loadExplosionAnimation()
        self.onSpawn()

    def loadExplosionAnimation(self):
        self.explosionFrames = []
        self.explosionCurrentFrame = 0
        frameWidth = 24
        for i in range(0, 6):
            self.explosionFrames.append(
                imageLoader(
                    "../images/Explode4.bmp",
                    3, # it's a big explode
                    (frameWidth * i,0,24,25)
                )
            )

    def onSpawn(self):
        self.reset()

    def onDeath(self):
        self.isWaitingToRespawn = True
        self.waitingToRespawn = RespawnDelay
        self.explosionCurrentFrame = 0

    def reset(self):
        self.rect.x = 400
        self.rect.y = 300
        self.velocityX = 0
        self.velocityY = 0
        self.accelerationX = 0
        self.accelerationY = 0
        self.collision = False

    def update(self):
        # process delayed events
        if self.isWaitingToRespawn:
            # Update explosion boom!
            # after plane crash
            # swap plane image to explode
            if self.explosionCurrentFrame < len(self.explosionFrames):
                self.image = self.explosionFrames[self.explosionCurrentFrame]
                # increase frame
                self.image.set_colorkey(self.explodeColorKey)
                self.explosionCurrentFrame +=  1
            else:
                self.image = pygame.Surface( (0, 0) )
            self.waitingToRespawn -= 1
            if self.waitingToRespawn <= 0:
                self.isWaitingToRespawn = False
                self.reset()
        else:
            # process input
            control = self.getPlayerInput()
            self.processControl(control)
            self.image = pygame.transform.rotate(self.asset,
                                                 self.angle)
            self.image.set_colorkey(self.planeColorKey)
            # collision detection
            self.checkForCollisions()
            self.updatePhysics()

    def checkForCollisions(self):
        for gameObject in self.collisionGroup:
            self.collision = self.rect.colliderect(gameObject.rect)
            if self.collision:
                self.onDeath()
                for gameObject in self.collisionGroup:
                    gameObject.onDeath()
                break


    def getPlayerInput(self):
        up = pygame.key.get_pressed()[pygame.K_UP]
        down = pygame.key.get_pressed()[pygame.K_DOWN]
        left = pygame.key.get_pressed()[pygame.K_LEFT]
        right = pygame.key.get_pressed()[pygame.K_RIGHT]

        return up,down,left, right


    def updatePhysics(self):
        self.velocityX += self.accelerationX
        self.velocityY += self.accelerationY

        # apply damping horizontal
        if self.velocityX < 0 - self.damping:
            self.velocityX += self.damping
        elif self.velocityX > 0 + self.damping:
            self.velocityX -= self.damping
        else:
            self.velocityX = 0
        # apply damping vertical
        if self.velocityY < 0 - self.damping:
            self.velocityY += self.damping
        elif self.velocityY > 0 +  self.damping:
            self.velocityY -= self.damping
        else:
            self.velocityY = 0

        # Cap velocity (Max)
        if self.velocityX > self.maxVelocity:
            self.velocityX = self.maxVelocity
        if self.velocityX < self.maxVelocity * -1:
            self.velocityX = self.maxVelocity * -1
        if self.velocityY > self.maxVelocity:
            self.velocityY = self.maxVelocity
        if self.velocityY < self.maxVelocity * -1:
            self.velocityY = self.maxVelocity * -1

        self.rect.x += self.velocityX
        self.rect.y += self.velocityY

    def processControl(self, control):
        # seems angle should be anticlockwise
        # only up
        if control[0] == 1 and control[1] == 0 and \
           control[2] == 0 and control[3] == 0:
            self.angle = 0
        # up and right
        elif control[0] == 1 and control[1] == 0 and \
           control[2] == 0 and control[3] == 1:
            self.angle = 315
        # only right
        elif control[0] == 0 and control[1] == 0 and \
           control[2] == 0 and control[3] == 1:
            self.angle = 270
        # down and right
        elif control[0] == 0 and control[1] == 1 and \
           control[2] == 0 and control[3] == 1:
            self.angle = 225
        # only down
        elif control[0] == 0 and control[1] == 1 and \
           control[2] == 0 and control[3] == 0:
            self.angle = 180
        # down and left
        elif control[0] == 0 and control[1] == 1 and \
           control[2] == 1 and control[3] == 0:
            self.angle = 135
        # only left
        elif control[0] == 0 and control[1] == 0 and \
           control[2] == 1 and control[3] == 0:
            self.angle = 90
        # left and up
        elif control[0] == 1 and control[1] == 0 and \
           control[2] == 1 and control[3] == 0:
            self.angle = 45

        # right - left
        self.accelerationX = self.thrust * (control[3] - control[2])
        # down - up
        self.accelerationY = self.thrust * (control[1] - control[0])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip, bounds, target, master):

        self.image = imageLoader(image, scale, clip)
        self.image.set_colorkey(0x454e5b)
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 500
        self.velocityX = 0
        self.velocityY = 0
        self.boundX = bounds[0]
        self.boundY = bounds[1]
        self.thrust = 0.2
        self.damping = 0.1
        self.maxVelocity = 5
        self.isWaitingToRespawn = False
        self.waitingToRespawn = 0
        self.target = target
        self.master = master
        self.reset()

    def onSpawn(self):
        self.reset()

    def onDeath(self):
        self.isWaitingToRespawn = True
        self.waitingToRespawn = RespawnDelay
        self.master.enemyHasDied()

    def reset(self):
        if self.master.allowSpawn():
            self.state = 1
            self.rect.x = random.randrange(0, self.boundX) * -1
            self.rect.y = random.randrange(0, self.boundY) * -1
            self.velocityX = 0
            self.velocityY = 0
            self.master.enemyHasSpawned()
        else:
            self.resetOffScreen()
            self.master.addWaitingSpawn(self)

    def resetOffScreen(self):
        self.rect.x = self.boundX
        self.rect.y = self.boundY

    def calcRange(self):
        return math.sqrt( (self.rect.x - self.target.rect.x)**2 +
                          (self.rect.y - self.target.rect.y)**2   )

    def processStates(self):
        # state 1 Search
        if self.state == 1:
            range = self.calcRange()
            if range <= 300:
                self.state = 2
            else:
                self.velocityX += self.thrust
                self.velocityY += self.thrust
        # state 2 chase player
        elif self.state == 2:
            range = self.calcRange()
            if range > 300:
                self.state = 3
            else:
                # get target vector
                targetVectorX = self.target.rect.x - self.rect.x
                targetVectorY = self.target.rect.y - self.rect.y
                distance = math.sqrt((0 - targetVectorX)**2 +
                                     (0 - targetVectorY)**2 )
                targetVectorX /= distance
                targetVectorY /= distance
                # apply thrust
                self.velocityX += targetVectorX * self.thrust
                self.velocityY += targetVectorY * self.thrust
        # state 3 lost
        elif self.state == 3:
            self.velocityX += self.thrust
            self.velocityY += self.thrust

    def update(self):
        if self.isWaitingToRespawn:
            self.waitingToRespawn -= 1
            if self.waitingToRespawn <= 0:
                self.isWaitingToRespawn = False
                self.reset()
        else:
            # little AI move
            self.processStates()
             # Cap velocity (Max)
            if self.velocityX > self.maxVelocity:
                 self.velocityX = self.maxVelocity
            if self.velocityX < self.maxVelocity * -1:
                self.velocityX = self.maxVelocity * -1
            if self.velocityY > self.maxVelocity:
                self.velocityY = self.maxVelocity
            if self.velocityY < self.maxVelocity * -1:
                self.velocityY = self.maxVelocity * -1

            # update enemy position
            self.rect.x += self.velocityX
            self.rect.y += self.velocityY

            if self.rect.x > self.boundX or self.rect.y > self.boundY:
                self.onDeath()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, image, scale, clip, bounds):
        self.image = imageLoader(image, scale, clip)
        self.image.set_colorkey(0x454e5b)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 250
        self.velocityX = 3
        self.velocityY = 3
        self.accelerationX = 0
        self.accelerationY = 0
        self.boundX = bounds[0]
        self.boundY = bounds[1]
        self.isWaitingToRespawn = False
        self.waitingToRespawn = 0
        self.onSpawn()

    def onSpawn(self):
        self.reset()

    def onDeath(self):
        self.isWaitingToRespawn = True
        self.waitingToRespawn = RespawnDelay

    def reset(self):
        self.rect.x = random.randrange(0, self.boundX) * -1
        self.rect.y = random.randrange(0, self.boundY) * -1

    def update(self):
        if self.isWaitingToRespawn:
            self.waitingToRespawn -= 1
            if self.waitingToRespawn <= 0:
                self.isWaitingToRespawn = False
                self.reset()
        else:
            self.velocityX += self.accelerationX
            self.velocityY += self.accelerationY
            self.rect.x += self.velocityX
            self.rect.y += self.velocityY

            if self.rect.x > self.boundX or self.rect.y > self.boundY:
                self.onDeath()


class WaveManager():
    def __init__(self):
        self.currentWave= 1
        self.enemySpawnedCount = 0
        self.enemyDeathCount = 0
        self.enemiesPerWave = 3
        self.waitingToSpawn = []
        self.score = 0

    def allowSpawn(self):
        if self.enemySpawnedCount >= self.enemiesPerWave:
            return False
        else:
            return True

    def enemyHasSpawned(self):
        self.enemySpawnedCount += 1

    def enemyHasDied(self):
        self.enemyDeathCount += 1
        self.score += 1

        if self.enemyDeathCount == self.enemiesPerWave:
            self.nextWave()
        else:
            pass

    def nextWave(self):
        self.currentWave += 1
        self.enemySpawnedCount = 0
        self.enemyDeathCount = 0
        self.enemiesPerWave += 3

    def addWaitingSpawn(self, gameObject):
        self.waitingToSpawn.append(gameObject)

    def update(self):
        if self.allowSpawn():
            for gameObject in self.waitingToSpawn:
                gameObject.reset()
