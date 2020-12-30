import pygame

pygame.init()

# Set up the drawing window
max_x = max_y = 500 
screen = pygame.display.set_mode([max_x, max_y])
font = pygame.font.SysFont(None, 24)


palla_x = 250
palla_y = 250
palla_vx = 0
palla_vy = 1
palla_r = 5

pad_x = 250
pad_y = 480
pad_vx = 0
pad_w = 50
pad_h = 5

score = 0

# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
          print ("KEYDOWN")
          if event.key == pygame.K_LEFT:
              pad_vx = -1
          elif event.key == pygame.K_RIGHT:
              pad_vx = 1
            

    # Fill the background with black
    screen.fill((0,0,0))

    # Draw a solid blue circle in the center
    palla_x = palla_x + palla_vx
    palla_y = palla_y + palla_vy
    pygame.draw.circle(screen, (0, 255, 0), (palla_x, palla_y), 2*palla_r)

    pad_x = pad_x + pad_vx
    if pad_x - pad_w/2 < 0: pad_x = pad_w/2
    if pad_x + pad_w/2 > max_x: pad_x = max_x - pad_w/2
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(pad_x-pad_w/2, pad_y, pad_w, pad_h))

    if palla_x + palla_r > max_x or palla_x - palla_r < 0: 
      palla_vx = -palla_vx
    if palla_y - palla_r < 0: 
      palla_vy = -palla_vy

    if palla_y  + palla_r> pad_y - pad_h/2: 
      if abs(palla_x - pad_x) < pad_w:
        score += 1
        dx = palla_x - pad_x
        dy = palla_y - pad_y
        dxy = (dx**2 + dy**2)**0.5
        palla_vx = 1. * dx/dxy
        palla_vy = 1. * dy/dxy
      else:
        palla_x = palla_y = 250
        palla_vy = -1
        palla_vx = 0
        score = 0
        

    img = font.render(str("Score: %04d" % score), True, (0,255,0))
    screen.blit(img, (20, 20))

    

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()

