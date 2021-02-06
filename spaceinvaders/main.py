import pygame
import os
import time
import random

pygame.init()
boom_fig = pygame.image.load(os.path.join("figs", "boom.png"))

SCREEN_W = 500
SCREEN_H = 500

screen = pygame.display.set_mode ((SCREEN_W,SCREEN_H))

running = True

class Patch:
  def __init__ (self, filename, center, size):
    self._fig = pygame.image.load (os.path.join("figs", filename))
    self._size = size
    self._center = center

    self._fig = pygame.transform.scale(self._fig, self._size)

  @property
  def center(self):
    return self._center

  @property
  def topleft(self):
    return self._center[0] - self._size[0]/2, self._center[1] - self._size[1]/2

  def draw_on (self, screen):
    screen.blit (self._fig, self.topleft)



class Ship (Patch):
  def __init__ (self, center=(SCREEN_W//2, SCREEN_H-40)):
    Patch.__init__ (self, "ship1.png", center, (40, 40))
    self.speed = 0
    self.last_update = None

  @property
  def x (self):
    return self._center[0]

  @x.setter
  def x(self, new_x):
    if new_x > self._size[0]/2 and new_x <  SCREEN_W - self._size[0]/2:
      self._center = (new_x, self._center[1])

  def update(self):
    if self.last_update is not None:
      self.x += self.speed * (time.time()-self.last_update)

    self.last_update = time.time()



class Alien (Patch):
  def __init__ (self, center=(SCREEN_W//2, 40), id=2):
    Patch.__init__ (self, "alien%d.png" % id, center, (50, 50))
    self.reset_chrono()

  def reset_chrono(self):
    self._chrono = time.time()

  @property
  def delta_t (self):
    return time.time() - self._chrono

  def update (self, status):
    if self.delta_t < .2:
      return False

    self.reset_chrono()
    if status == 'right':
      self._center = (self.center[0] + 20, self.center[1])
      return (self._center[0] > SCREEN_W - 50)
    elif status == 'left':
      self._center = (self.center[0] - 20, self.center[1])
      return (self._center[0] < 50)
    elif status == 'down':
      self._center = (self.center[0] , self.center[1]+15)
      return True


class Projectile (Patch):
  def __init__ (self, figure, position, speed):
    Patch.__init__ (self, figure, position, (20, 20))
    self.speed = speed
    self.last_update = None

  def update(self):
    if self.last_update is not None:
      self._center = (
              self._center[0] + self.speed[0] * (time.time() - self.last_update),
              self._center[1] + self.speed[1] * (time.time() - self.last_update)
      )

    self.last_update = time.time()

  def check_overlap_with (self, something):
    xover = abs(self._center[0] - something._center[0]) < (self._size[0] + something._size[0])/3
    yover = abs(self._center[1] - something._center[1]) < (self._size[1] + something._size[1])/3
    if xover and yover:
      return True


class Rocket (Projectile):
  def __init__ (self, position, speed=(0,-200)):
    Projectile.__init__ (self, "razzo.png", position, speed)

class Bomb (Projectile):
  def __init__ (self, position, speed=(0,100)):
    Projectile.__init__ (self, "bomb.png", position, speed)



ship = Ship()
projectiles = list()


def create_aliens ():
  ret = list()
  for iX in range(5):
    for iY in range(4):
      ret.append (Alien ( (iX * 55 + 40, iY * 45 +40), iY+1) )

  return ret

aliens = create_aliens()

status = "right"
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_LEFT:
        ship.speed += -150
      elif event.key == pygame.K_RIGHT:
        ship.speed += +150
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_LEFT:
        ship.speed -= -150
      elif event.key == pygame.K_RIGHT:
        ship.speed -= +150
      elif event.key == pygame.K_SPACE:
        projectiles.append(Rocket(ship.center, (0, -300)))


  screen.fill((0,0,0))

  ship.update()
  ship.draw_on (screen)


  updates = [alien.update(status) for alien in aliens]
  for alien in aliens:
    alien.draw_on (screen)

    if random.randint(0, 1000) == 0:
      projectiles.append (Bomb(alien._center, (0,random.randint(70,110))))


  if any(updates):
    if status=="left": status = "right"
    elif status=="right": status = "down"
    elif status=="down": status = "left"

  destroy_projectiles = list()
  destroy_aliens = list()
  for projectile in projectiles:
    projectile.update()
    projectile.draw_on(screen)

    if projectile.__class__ == Rocket:
      for alien in aliens:
        if projectile.check_overlap_with(alien):
          destroy_aliens.append(alien)
          destroy_projectiles.append(projectile)
          break
      if projectile in destroy_projectiles:
        break
    elif projectile.__class__ == Bomb:
      if projectile.check_overlap_with(ship):
        screen.fill ((255,0,0))
        screen.blit(boom_fig, (50, 50))
        pygame.display.flip()
        projectiles = list()
        destroy_projectiles = list()
        destroy_aliens = list()
        aliens = create_aliens()
        time.sleep(1)
        break




  for proj in destroy_projectiles:
    del projectiles[projectiles.index(proj)]

  for alien in destroy_aliens:
    del aliens[aliens.index(alien)]

    if len(aliens) == 0:
      status = "right"
      projectiles = list()
      aliens = create_aliens()


  pygame.display.flip()
      
pygame.quit()
