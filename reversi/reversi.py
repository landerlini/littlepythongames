"""
Reversi
-------

The board game "Reversi", more known as Othello, is a simple, yet challenging, 
board game for two players.
https://en.wikipedia.org/wiki/Reversi
"""
import pygame 
import numpy as np
from threading import Thread 
import time 


_LAST_CELL_CLICKED_ = None 
board_image = pygame.image.load ( "figs/reversi_board.png" )
white_piece = pygame.image.load ( "figs/reversi_white.png" )
black_piece = pygame.image.load ( "figs/reversi_black.png" )



class Game (Thread):
  """
    Raversi game flow running in a separate thread with respect to 
    the graphic user interface.
  """
  def __init__ (self):
    """
      Initialize the game
    """
    self.white = np.zeros ((8,8), dtype = np.float32)
    self.black = np.zeros ((8,8), dtype = np.float32)

    self.white[3,3]=1.
    self.white[4,4]=1.
    self.black[3,4]=1.
    self.black[4,3]=1.

    Thread.__init__(self) 
    self._status = None 

  def run (self):
    """
      As defined in the Thread interface, run defines the function 
      running in parallel to the main program. 
  
      Here, it defines the overall game flow:
        if white can move
          propose a move untill the proposed move is valid
          update the board consequently 

        if black can move
          propose a move untill the proposed move is valid
          update the board consequently 
        
        if neither white nor black can move
          the match is over
          compute the winner
    """
    self._running = True 
    while self._running: 

      if len(self.list_valid_move(self.white,self.black))>0: 
        valid = False
        while not valid:
          w0, b0 = self.white.copy(), self.black.copy() 
          w, b = self.white_moves (w0, b0)
          ## This is a hook for immediate termination of the game flow on stop
          if not self._running: return 
          valid = self.check_valid (w, b, w0, b0, 'white')
        self.white, self.black = self.move_outcome (w, b, w0, b0) 

      if len(self.list_valid_move(self.black,self.white))>0: 
        valid = False
        while not valid:
          w0, b0 = self.white.copy(), self.black.copy() 
          w, b = self.black_moves (w0, b0)
          ## This is a hook for immediate termination of the game flow on stop
          if not self._running: return 
          valid = self.check_valid (w, b, w0, b0, 'black')
        self.black, self.white = self.move_outcome (b, w, b0, w0)


      white_lives = len(self.list_valid_move(self.white,self.black))>0
      black_lives = len(self.list_valid_move(self.black,self.white))>0
      if not white_lives and not black_lives:
        self.choose_winner ( self.white, self.black ) 
        self._running = False 


  def stop(self): 
    "Interrupt the game"
    self._running = False 
    self.join() 


  def white_moves (self, w0, b0):
    "Function defining the white move, can be overridden to implement AI"
    self._status = "White moves"
    global _LAST_CELL_CLICKED_
    _LAST_CELL_CLICKED_ = None
    while _LAST_CELL_CLICKED_ is None and self._running:
      time.sleep(.1)
    
    w, b = w0.copy(), b0.copy()
    w[_LAST_CELL_CLICKED_] = 1
    self._status = None
    return w, b


  def black_moves (self, w0, b0):
    "Function defining the black move, can be overridden to implement AI"
    self._status = "Black moves"
    global _LAST_CELL_CLICKED_
    _LAST_CELL_CLICKED_ = None
    while _LAST_CELL_CLICKED_ is None and self._running:
      time.sleep(.1)

    w, b = w0.copy(), b0.copy()
    b[_LAST_CELL_CLICKED_] = 1
    self._status = None
    return w, b


  @property
  def status (self):
    "Read-only game status"
    return self._status 


  def list_valid_move (self, player, opponent):
    """
    Runs over all the empty cells checking whether they are viable optoins
    for a player's move. Returns the indices for the valid cells
    """
    ret = [] 
    for i in range(8):
      for j in range(8):
        if player[i,j] == 0 and opponent[i,j] == 0:
          p, o = player.copy(), opponent.copy()
          p[i,j] = 1
          if self._check_for_updates (p, o, player, opponent):
            ret.append ( (i,j) )

    return ret 
          
          
  def _check_for_updates (self, p, o, p0, o0):
    """
    In reversi a valid move is a move with an outcome. This function evaluates
    the outcome of the move in a sandbox and return True if at least one token
    was reversed. 
    """
    pn, on = self.move_outcome (p, o, p0, o0) 
    if np.all (p == pn) and np.all (o == on): 
      return False
    return True
      

  def move_outcome (self, p, o, p0, o0):
    """
    Compute the outcome of a move by reversing the required tokens.
    """
    p = p.copy() 
    o = o.copy() 

    iX, iY = np.indices ((8,8)) 
    new = (p-p0).astype(np.bool) 
    i, j = iX [new], iY [new] 
    pos = np.array([i,j]).reshape(-1)

    directions = np.array([
      [ 1,  0],
      [ 0,  1],
      [-1,  0],
      [ 0, -1],
      [ 1,  1],
      [ 1, -1],
      [-1,  1],
      [-1, -1],
    ]) 

    for delta in directions:
      while True: 
        updated = False  
        for n in range(1,8):
          tp = pos+delta*(n+1)
          to = pos+delta*n
          if np.max(tp) > 7 or np.max(to) > 7: continue 
          if np.min(tp) < 0 or np.min(to) < 0: continue 
          if o[to[0], to[1]] == 0: break 
          
          if o[to[0], to[1]] > 0 and p[tp[0], tp[1]] > 0:
            p[to[0], to[1]] = 1
            o[to[0], to[1]] = 0
            updated = True 
      
        if not updated: 
          break 

    return p, o 
      
    

  def check_valid (self, w, b, w0, b0, player):
    """
    Validates the input defining a new move. It checks:
     - only the player's board has changed 
     - one and only one piece was added to the player's board 
     - the move has an outcome  

    Returns True on a valid move
    """
    ## Constantness of the other board 
    if player == 'white' and np.any(b0 != b): return False 
    if player == 'black' and np.any(w0 != w): return False 

    ## Number of new items
    if player == 'white' and np.count_nonzero(w - w0) != 1: return False 
    if player == 'black' and np.count_nonzero(b - b0) != 1: return False 


    iX, iY = np.indices ((8,8)) 

    if player == 'white':
      new = (w - w0).astype (np.bool) 
      if b0[new]: 
        return False 

      return self._check_for_updates (w, b, w0, b0) 
      
    if player == 'black':
      new = (b - b0).astype (np.bool) 
      if w0[new] == 1: 
        return False 

      return self._check_for_updates (b, w, b0, w0)
      
    return True 
       

  def choose_winner (self, white, black):
    """
    Counts the number of black and white tokens and choose the winner
    """
    nw = np.count_nonzero (white)
    nb = np.count_nonzero (black)
    if nw > nb:
      self._status = "White wins" 
      return "white"
    elif nb > nw:
      self._status = "Black wins" 
      return "black"
    else:
      self._status = "Parity" 
      return "parity"
    
      




################################################################################
## Graphic user interface (GUI)

def pos2cell (pos):
  "Convert the position on the screen to the cell coordinates"
  x, y = pos
  iX, iY = ((x-27)//62, (y-27)//62) 
  if iX > 7: iX = 7
  if iY > 7: iY = 7
  if iX < 0: iX = 0
  if iY < 0: iY = 0
  return iX, iY 

def cell2pos (cell):
  "Convert the cell coordinates to the top-left corner of the cell on screen"
  iX, iY = cell
  return (iX*62 + 27, iY*62 + 29)

def draw_board (screen, white, black):
  "Draw the board and the tokens"
  screen.blit(board_image, (0,0))
  for iX in range(8):
    for iY in range(8):
      if black[iX][iY] > 0 and white[iX][iY] > 0:
        raise ValueError ("Cell (%d,$d) both black and white"%(iX, iY))
      elif white[iX][iY] > 0:
        screen.blit (white_piece, cell2pos ((iX, iY)))   
      elif black[iX][iY] > 0:
        screen.blit (black_piece, cell2pos ((iX, iY))) 



def play(GameClass):
  """
  Entry point for playing the game. 
  Takes a class inheriting from reversi.Game as argument.
  """
  global _LAST_CELL_CLICKED_

  ## Initialize the screen 
  pygame.init()
  font = pygame.font.SysFont(None, 24)
  max_x = max_y = 550 
  screen = pygame.display.set_mode([max_x, max_y])

  ## Initialize the game flow
  game = GameClass()
  game.start() # here it branches the logic flow spawning a separate thread

  running = True
  while running:
      for event in pygame.event.get():  ## React to "exit"
          if event.type == pygame.QUIT:
              running = False
              game.stop() ## Interrupts the game-flow thread 
          if event.type == pygame.MOUSEBUTTONUP:
              _LAST_CELL_CLICKED_ = pos2cell(pygame.mouse.get_pos()) 
              if game._running is False:
                game = GameClass()
                game.start() 

      ## Updates the board 
      screen.fill((0,0,0))
      draw_board (screen, game.white, game.black)

      ## Writes the game status on the top-left corner
      if game.status is not None:
        text = font.render(game.status, True, (0,255,0))
        screen.blit(text, (2, 2))

      time.sleep(.02)

      # Flip the display
      pygame.display.flip()
          

  # Done! Time to quit.
  pygame.quit()

if __name__ == '__main__':
  play(Game) 
