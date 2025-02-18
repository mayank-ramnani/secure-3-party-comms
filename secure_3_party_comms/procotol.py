from random import randint, randrange, choices
from tqdm import tqdm
import os, contextlib
import random
import numpy as np
import pandas as pd

#GLOBALS
DEBUG = True
UNDELIVERED_QUEUE = [] #Queuefor undelivered messages for simulation
MESSAGE_QUEUE = []
PADS = []       #PADS[i] is for the ith client, each client will have the ith mutable copy
ROOT_PADS = []  #Each client will have a constant fixed ROOT_PADS copy
UNDELIVERED_PROBABILITY_RANGE = (5,25) #x to y% chance of a message being undelivered
UNDELIVERED_COUNT = 0
COLLISIONS = [0,0,0]

M = 3           #Total clients in the network
N = 12         #Available pads [user input]
D = 2          #Max undelivered messages at any point [user input]

def init_globals():
    global DEBUG, UNDELIVERED_QUEUE, MESSAGE_QUEUE, PADS, ROOT_PADS, UNDELIVERED_COUNT, M, N, D, COLLISIONS
    UNDELIVERED_QUEUE.clear()
    MESSAGE_QUEUE.clear()
    UNDELIVERED_COUNT = 0
    COLLISIONS = [0,0,0]
    PADS.clear()
    ROOT_PADS.clear()

    # Initialize pads
    pad_set = set()
    while len(pad_set) < N:
        pad_set.add(randint(2**16, 2**32 - 2))
    ROOT_PADS.extend(pad_set)

    print(f"Initialized: M={M}, N={N}, D={D}, DEBUG={DEBUG}")

def init_pads(n,m):
  pads = []
  for x in range(n):
    pad = -1
    while pad == -1 or pad in pads:
      pad = randint(2**16,2**32-2)
    pads.append(pad)
  return pads

def suppress_all_output(func, *args, **kwargs):
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            return func(*args, **kwargs)

def undelivered():
    """Returns True with a varying probability between 5% and 15%."""
    probability = randint(UNDELIVERED_PROBABILITY_RANGE[0],UNDELIVERED_PROBABILITY_RANGE[1])  # Pick a random probability between 20% and 50%
    return randint(1, 100) <= probability and len(UNDELIVERED_QUEUE) < D # Compare with a 100-sided dice roll

class client:
  def __init__(self, name, pads, messages_to_send = []):
    self.name = name  #A,B,C
    self.ROOT_PADS = pads.copy() #const
    self.pads = pads.copy()
    self.others = ['A', 'B', 'C']
    self.others.remove(self.name)

    if messages_to_send:
      self.messages_to_send = messages_to_send
    else:
      self.messages_to_send = [randint(1, 2**32-1) for _ in self.ROOT_PADS]

    self.messages_sent = []
    self.received_messages = {self.others[0]:[], self.others[1]:[]}
    self.undelivered_B = 0

  def print_history(self):
      print(f"\n{'='*40}")
      print(f"📜 History for {self.name}")
      print(f"{'='*40}")

      print("\n📤 Messages Sent:")
      if self.messages_sent:
          for i, msg in enumerate(self.messages_sent, 1):
              print(f"  {i}. Message: {msg['message']}, Token Index: {msg['token_index']}")
      else:
          print("  No messages sent.")

      print("\n📥 Messages Received:")
      if any(self.received_messages.values()):
          for sender, msgs in self.received_messages.items():
              print(f"  From {sender}:")
              for i, msg in enumerate(msgs, 1):
                  print(f"    {i}. Message: {msg['message']}, Token Index: {msg['token_index']}")
      else:
          print("  No messages received.")

      print(f"{'='*40}\n")


  def statistics(self, Print = True):

    sent_count = len(self.messages_sent)
    received_count = sum(len(x) for x in self.received_messages.values())
    undelivered_count = len([x for x in UNDELIVERED_QUEUE if x['sender'] == self.name])

    if Print:
        print(f"\n{'='*40}")
        print(f"📊 Statistics for {self.name}")
        print(f"{'='*40}")

        print(f"📤 Messages Sent:      \t\t{sent_count}")
        print(f"📥 Messages Received:  \t\t{received_count}")
        print(f"🚫 Messages Undelivered:\t{undelivered_count}")

        print(f"{'='*40}\n")

    return (sent_count, received_count, undelivered_count)


  def receive_message(self, sender, token_index, message):
    global COLLISIONS

    try:
      local_token_index = self.pads.index(self.ROOT_PADS[token_index])
      if sender == 'A':
        self.pads = self.pads[local_token_index+1:]
      elif sender == 'B':
        if local_token_index != len(self.pads)//2:
          #there was atleast 1 undelivered message by B
          self.undelivered_B += abs(local_token_index - len(self.pads)//2)
          pass
        self.pads = self.pads[:local_token_index] + self.pads[local_token_index+1:]
      elif sender == 'C':
        self.pads = self.pads[:local_token_index]
    except ValueError as e:

      if DEBUG:
        print(f'[C] \t COLLISION\t SENDER: {sender}\t Receiver: {self.name} \tToken index: {token_index}\
        \t Token:{self.ROOT_PADS[token_index]} \tMessage: {message}\t Error:', e)

      COLLISIONS[0 if sender == 'A' else 1 if sender == 'B' else 2] += 1
    # token_used = self.pads.pop(token_index)
    token_used = self.ROOT_PADS[token_index]
    if DEBUG:
      print(f'[R]\t Receiver: {self.name}\t Cipher: {message}\t Token: {token_used}\t Message: {message^token_used}')
    message ^= token_used
    self.received_messages[sender].append({'message': message, 'token_index':token_index})
    return token_used

  def _send_message(self, token_index):
    token_used = self.pads.pop(token_index)
    token_index = self.ROOT_PADS.index(token_used)
    message = self.messages_to_send.pop(0)
    self.messages_sent.append({'message': message, 'token_index':token_index})
    if DEBUG:
      print(f'[S]\tSender: {self.name}\t Message: {message}\t Token: {token_used}\t Cipher: {message^token_used}')
    message ^= token_used
    MESSAGE_QUEUE.append({'sender':self.name, 'message': message, 'token_index':token_index})
    return token_used

  def send_message(self):
    assert len(self.pads) > (2*D + D//2*2)#+ self.undelivered_B//2 + (M)), f"{self.name}: Not enough pads left! Available: {len(self.pads)}"
    # assert self.can_send()
    if self.name == 'A':
      self._send_message(0)
    elif self.name == 'B':
      self._send_message(len(self.pads)//2)
    elif self.name == 'C':
      self._send_message(len(self.pads) - 1)

class queue_handler:
  def __init__(self, clients):
    self.clients = {'A': clients[0], 'B': clients[1], 'C': clients[2]}


  def deliver(self):
    '''
    Delivers messages from the queue
    '''
    global UNDELIVERED_COUNT
    while MESSAGE_QUEUE:
      message = MESSAGE_QUEUE.pop(0)
      if undelivered():
        UNDELIVERED_COUNT += 1
        if DEBUG:
          print('[U] UNDELIVERED')
        UNDELIVERED_QUEUE.append(message)
      else:
        sender = message['sender']
        receivers = ['A','B','C']
        receivers.remove(sender)
        token_index = message['token_index']
        message = message['message']

        for receiver in receivers:
          self.clients[receiver].receive_message(sender, token_index, message)

  def deliver_undelivered(self):
    '''
    Delivers undelivered messages from the queue, each message has 50 to 90% chance of being delivered
    '''
    while UNDELIVERED_QUEUE:
      message = UNDELIVERED_QUEUE.pop(0)
      probability = randint(50, 90)
      if randint(1, 100) <= probability:
        sender = message['sender']
        receivers = [x for x in ['A', 'B', 'C'] if x != sender]
        token_index = message['token_index']
        message = message['message']

        for receiver in receivers:
          self.clients[receiver].receive_message(sender, token_index, message)
      else:
        MESSAGE_QUEUE.append(message)
