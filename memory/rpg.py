import pygame 
pygame.init()
font = pygame.font.SysFont(None, 24)
max_x = max_y = 550 
screen = pygame.display.set_mode([max_x, max_y])

character = pygame.image.load ( "figs/character.png" ) 
running = True

################################################################################
## Base class 
class DisplayedElement:
  image = None
  def __init__ (self, screen, position):
    self.position = position
    self.screen = screen 

  @property
  def shape (self):
    return list(self.image.get_rect()[-2:]) 

  def get_coords (self):
    w, h = self.shape
    return (self.position[0]-0.5)*50, (self.position[1]-0.5)*50


################################################################################
## Character class 
class Character (DisplayedElement):
  image = pygame.image.load ( "figs/character.png" )
  def __init__ (self, screen):
    self.direction = "E"
    DisplayedElement.__init__(self, screen, (0,0))

  @property
  def angle (self):
    if   self.direction == 'N': return   0
    elif self.direction == 'W': return 270
    elif self.direction == 'S': return 180
    elif self.direction == 'E': return  90
    
  def update (self):
    image = pygame.transform.rotate(self.image, self.angle)
    self.screen.blit (image, self.get_coords()) 


################################################################################
## Box class 
class Box(DisplayedElement):
  image_active = pygame.image.load ("figs/box_open.png")
  image = pygame.image.load ("figs/box_closed.png")
  def __init__ (self, screen, content, position):
    self.active = False 
    self.opened = False 
    self.content = content 
    DisplayedElement.__init__(self, screen, position)

  def update (self):
    image = self.image_active if self.status else self.image
    self.screen.blit (image, self.get_coords()) 

    if self.status: 
      img = font.render(str(self.content), True, (80,255,80) if self.opened else (255,80,80))
      x,y = self.get_coords()
      screen.blit(img, (x+15,y+10))

  @property
  def status (self):
    return self.active or self.opened 
    
  def activate (self):
    self.active = True 
    return self.content

  def deactivate (self):
    self.active = False


################################################################################
## Load level from file
def get_boxes (filename):
  boxes = []
  ifile = open(filename)
  for y, line in enumerate(ifile):
    for x, digit in enumerate(line[:-1]):
      if digit != "_": 
        boxes.append ( Box(screen, digit, (x+1,y+1)) )
  return boxes 
    


last_box = None 
################################################################################
## Processing the user interactions (keystrokes)
def process_event (character, event, forbidden_spots=[]):
  global last_box

  if event.type != pygame.KEYDOWN:
    return 

  for box in boxes:
    box.deactivate() 


  ### Moving around 
  x0, y0 = character.position 
  if event.key == pygame.K_UP:
    character.direction = "N"
    if (x0, y0-1) not in forbidden_spots:
      character.position = (x0, max(1, y0-1))
  elif event.key == pygame.K_LEFT:
    character.direction = "E"
    if (x0-1, y0) not in forbidden_spots:
      character.position = (max(1, x0-1), y0)
  elif event.key == pygame.K_DOWN:
    character.direction = "S"
    if (x0, y0+1) not in forbidden_spots:
      character.position = (x0, min(10, y0+1))
  elif event.key == pygame.K_RIGHT:
    character.direction = "W"
    if (x0+1, y0) not in forbidden_spots:
      character.position = (min(10, x0+1), y0)

  ### Interacting with boxes 
  elif event.key == pygame.K_SPACE:
    if   character.direction == 'N': x,y = x0,y0-1
    elif character.direction == 'E': x,y = x0-1,y0
    elif character.direction == 'S': x,y = x0,y0+1
    elif character.direction == 'W': x,y = x0+1,y0
    for box in boxes:
      if box.position == (x,y):
        ## Memory-game logics 
        if last_box is not None and box != last_box and last_box.content == box.content:
          last_box.opened = True 
          box.opened = True 

        box.activate() 
        last_box = box
         
      
################################################################################
## Game entry-point 

## create character 
character = Character(screen)
character.position = (1, 1)

## define level files 
levels = iter(["rpg_1.dat", "rpg_2.dat", "rpg_3.dat"]*100) 

## loads the next level in the list (the first one at this time)
boxes = get_boxes(next(levels))
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        ## Demand to the process_event functon the processing of 
        ## each keystroke
        process_event (character, event,
          forbidden_spots = [b.position for b in boxes]
        ) 
            
    # Fill the background with black
    screen.fill((200,200,200))

    character.update() 
    for box in boxes:
      box.update() 
    
    if all([box.opened for box in boxes]):
      boxes = get_boxes(next(levels)) 
      character.position = (1,1)
      last_box = None
    
    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()

