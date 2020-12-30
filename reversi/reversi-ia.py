"""
This module define three simple artificial intelligence strategies for reversi:
 - random moves
 - weighted random moves (borders are more appealing)
 - deep neural network 


The strategies are called "agents". An additional agent is defined for 
"human" decision on the moves. 
An agent is a callable that takes a Game instance as input, together with 
the board of the player's and opponent's tokens. 
In the case of the neural network agent, the callable is class which holds 
the necessary configurations of the neural network.

A class GameAi inherits from reversi.Game and implements the definition
of two agents for both the white and the black players.

The argparse module is used to setup the match from command line
"""
import tensorflow as tf
import reversi 
import numpy as np 

import argparse 

################################################################################
## Random agent
def random_agent (game, player, opponent):
  moves = game.list_valid_move(player, opponent) 
  index = np.random.choice (len(moves)) 
  i, j = moves [index] 
  player_ = player.copy()
  player_[i,j] = 1
  return player_, opponent 

################################################################################
## Border-enhanced agent (tactics)
def tactics_agent (game, player, opponent):
  moves = game.list_valid_move(player, opponent) 
  w = np.ones ( len(moves) ) 
  for n, (i, j) in enumerate(moves):
    if i == 0 or i  == 7:
      w[n] *= 2
    if j == 0 or j  == 7:
      w[n] *= 2
      
  index = np.random.choice (len(moves), p=w/np.sum(w)) 
  i, j = moves [index] 
  player_ = player.copy()
  player_[i,j] = 1
  return player_, opponent 


################################################################################
## Neural-network based agent
class NeuralNetwork_agent:
  def __init__ (self, name):
    self.name = name 
    self.net = tf.keras.models.Sequential()
    self.net.add (tf.keras.layers.Input(8*8*2, dtype=np.float32))
    self.net.add (tf.keras.layers.Flatten())
    self.net.add (tf.keras.layers.Dense(256, activation = 'tanh'))
    self.net.add (tf.keras.layers.Dense(256, activation = 'tanh'))
    #self.net.add (tf.keras.layers.Dense(16, activation = 'tanh'))
    self.net.add (tf.keras.layers.Dense(1)) 
    self.net.compile (tf.keras.optimizers.Adam(1e-3), tf.keras.losses.MeanSquaredError())
    self.batch = [] 
    self.oppbatch = [] 


  def __call__ (self, game, player, opponent):
    moves = game.list_valid_move(player, opponent) 
    best_score = -1000000
    best_move = 0
    best_player, best_opponent = None, None
    for iMove, (i, j) in enumerate(moves): 
      p0, o0 = player.copy(), opponent.copy()
      p, o = player.copy(), opponent.copy()
      p[i,j] = 1
      p1, o1 = p.copy(), o.copy()
      p1, o1 = game.move_outcome (p1, o1, p0, o0) 
      move = np.stack((p1,o1)).reshape((1,-1))
      new_score = self.net(move)
      if new_score > best_score: 
        best_score = new_score 
        best_move  = p, o
        best_player   = p1
        best_opponent = o1

    self.batch.append (np.stack((best_player, best_opponent)).reshape(-1))
    self.batch.append (np.stack((best_player[::-1], best_opponent[::-1])).reshape(-1))
    self.batch.append (np.stack((best_player[:,::-1], best_opponent[:,::-1])).reshape(-1))
    self.batch.append (np.stack((best_player[::-1,::-1], best_opponent[::-1,::-1])).reshape(-1))
    self.batch.append (np.stack((best_player.T, best_opponent.T)).reshape(-1))
    self.batch.append (np.stack((best_player.T[::-1], best_opponent.T[::-1])).reshape(-1))
    self.batch.append (np.stack((best_player.T[:,::-1], best_opponent.T[:,::-1])).reshape(-1))
    self.batch.append (np.stack((best_player.T[::-1,::-1], best_opponent.T[::-1,::-1])).reshape(-1))

    best_opponent, best_player = best_player, best_opponent 
    self.oppbatch.append (np.stack((best_player, best_opponent)).reshape(-1))
    self.oppbatch.append (np.stack((best_player[::-1], best_opponent[::-1])).reshape(-1))
    self.oppbatch.append (np.stack((best_player[:,::-1], best_opponent[:,::-1])).reshape(-1))
    self.oppbatch.append (np.stack((best_player[::-1,::-1], best_opponent[::-1,::-1])).reshape(-1))
    self.oppbatch.append (np.stack((best_player.T, best_opponent.T)).reshape(-1))
    self.oppbatch.append (np.stack((best_player.T[::-1], best_opponent.T[::-1])).reshape(-1))
    self.oppbatch.append (np.stack((best_player.T[:,::-1], best_opponent.T[:,::-1])).reshape(-1))
    self.oppbatch.append (np.stack((best_player.T[::-1,::-1], best_opponent.T[::-1,::-1])).reshape(-1))

    return best_move
    

  def train_step (self, label, nEpochs=1):
    for iEpoch in range(nEpochs):
      self.net.train_on_batch (np.array(self.batch), np.full(len(self.batch), label))
      self.net.train_on_batch (np.array(self.oppbatch), np.full(len(self.batch), -label))
    self.batch = [] 
    self.oppbatch = [] 

  def save(self):
    self.net.save(self.name) 

  @staticmethod 
  def load(name):
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),name)
    net = NeuralNetwork_agent(name)
    net.net = tf.keras.models.load_model(path) 
    return net 
    
    
      

################################################################################
## Class inheriting from reversi.Game, but opening to the definition of 
## two agents for the white and black players. 
## If white_agent == 'human' and black_agent == 'human', then GameAi is 
## identical to Game. Otherwise, the respective agents are invoked to 
## define the moves of the two players. 
class GameAi (reversi.Game):
  def __init__ (self, white_agent, black_agent):
    self.white_agent = white_agent
    self.black_agent = black_agent 
    reversi.Game.__init__(self) 

  def white_moves (self, w0, b0):
    if self.white_agent == 'human': return reversi.Game.white_moves(self, w0, b0) 
    w, b = self.white_agent (self, w0, b0) 
    return w,b

  def black_moves (self, w0, b0):
    if self.black_agent == 'human': return reversi.Game.black_moves(self, w0, b0) 
    b, w = self.black_agent (self, b0, w0) 
    return w,b 



if __name__ == '__main__':
  nn = NeuralNetwork_agent("reversiNN") 
  agents = dict(
    random=random_agent, 
    tactics=tactics_agent, 
    human="human", 
    train=nn, 
    nnet=NeuralNetwork_agent.load('reversiNN'), 
  )

  parser = argparse.ArgumentParser()
  parser.add_argument ("-w", "--white", default = "human", choices = agents.keys())
  parser.add_argument ("-b", "--black", default = "random", choices = agents.keys())
  parser.add_argument ("-q", "--quiet", action='store_true')
  cfg = parser.parse_args() 

  if cfg.quiet and (cfg.white == 'human' or cfg.black == 'human'):
    raise ValueError ("Cannot play in batch mode with human agent") 
 
  from functools import partial 
  MyGame = partial(GameAi, white_agent=agents[cfg.white], black_agent=agents[cfg.black]) 


  if cfg.quiet:
    tot_b = 0
    tot_w = 0
    while True: 
      g = MyGame()
      g.run() 
      nb = np.count_nonzero(g.black)
      nw = np.count_nonzero(g.white)
      if nb>nw:
        tot_b += 1
      elif nw>nb: 
        tot_w += 1

      if cfg.white == 'train': 
        nn.train_step ( nw - nb ) 
      if cfg.black == 'train': 
        nn.train_step ( nb - nw ) 
      
      ## Don't save quick tests 
      if tot_b + tot_w > 100:
        nn.save()

    
      print ("%15s: %d white - %d black" % ( g.status, tot_w, tot_b )) 
  else: 
    reversi.play(MyGame) 
    

