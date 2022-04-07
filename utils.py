import socket
import time

def byte(n):
  return bytes([n])

def isint(s):
  try:
    int(s)
    return True
  except:
    return False

class RetriableSocket:
  def __init__(self, addr):
    self.sock = socket.socket()
    self.sock.connect(addr)
  
  def close(self):
    self.sock.close()
  
  def send(self, s):
    if isinstance(s, int): s = byte(s)
    if isinstance(s, str): s = s.encode('utf-8')
    i = 0
    while i < len(s): i += self.sock.send(s[i:])
  
  def recv(self, n):
    data = b''
    while len(data) < n: data += self.sock.recv(n - len(data))
    return data

class IEmulatorClient:
  def disconnect(self): pass
  def subscribe(self, channel): pass
  def unsubscribe(self, channel): pass
  
  def send(self, channel, msg):
    raise Exception('IEmulatorClient::send')
  
  def recv(self):
    raise Exception('IEmulatorClient::recv')

class StemClient(IEmulatorClient):
  def __init__(self):
    self.sock = RetriableSocket(('stem.fomalhaut.me', 5733))
  
  def disconnect(self):
    if self.sock:
      self.sock.close()
      self.sock = None
  
  def send_package(self, _type, _id, _message=None):
    pack = byte(_type)
    if _type == 3 or _type == 4:
      pack += _id
    else:
      pack += byte(len(_id))
      pack += _id.encode('utf-8')
      if _message: pack += _message.encode('utf-8')
    
    self.sock.send(len(pack) // 256)
    self.sock.send(len(pack) % 256)
    self.sock.send(pack)
  
  def subscribe(self, channel):
    self.send_package(1, channel)
  
  def unsubscribe(self, channel):
    self.send_package(2, channel)
  
  def send(self, channel, msg):
    self.send_package(0, channel, msg)
  
  def recv(self):
    pack_len = self.sock.recv(2)
    pack_type = self.sock.recv(1)
    
    if pack_type == b'\0': # incoming msg
      ch_len = self.sock.recv(1)[0] # getting int from byte string
      ch_id = self.sock.recv(ch_len)
      
      msg_len = pack_len[0] * 256 + pack_len[1]
      msg_len -= ch_len + 2
      msg = self.sock.recv(msg_len)
      
      return str(msg, 'utf-8')
    elif pack_type == b'\3': # pinging
      msg_len = pack_len[0] * 256 + pack_len[1] - 1
      self.send_package(4, self.sock.recv(msg_len))
      
      return None

class TerminalClient(IEmulatorClient):
  def send(self, channel, msg):
    prefix = '%s> ' % channel
    for line in msg.split('\n'):
      print(prefix + line)
      prefix = ' ' * len(prefix)
  
  def recv(self):
    return input('mov-emu> ')

class StaticClient(IEmulatorClient):
  def __init__(self):
    with open(__file__ + '/../code.txt') as f:
      self.text = f.read().lstrip()
  
  def send(self, channel, msg):
    prefix = '%s> ' % channel
    for line in msg.split('\n'):
      print(prefix + line)
      prefix = ' ' * len(prefix)
  
  def recv(self):
    first_line, self.text = self.text.split('\n', 1)
    if first_line == 'stop':
      input('\n(stopping)')
    return first_line

class ClientsSelector:
  stat = StaticClient
  stem = StemClient
  term = TerminalClient

class Queue:
  def __init__(self):
    self.q_pushed = []
    self.q_popped = []
    self.commands = {}
  
  def contains(self, v):
    return v in self.commands
  
  def push(self, v):
    if self.contains(v): return
    self.commands[v] = []
    self.q_pushed.append(v)
  
  def pop(self):
    if not self.q_popped:
      while self.q_pushed:
        self.q_popped.append(self.q_pushed.pop())
    
    v = self.q_popped.pop()
    del self.commands[v]
    return v
  
  def back(self):
    if self.q_popped: return self.q_popped[-1]
    if self.q_pushed: return self.q_pushed[0]
    return None
  
  def push_command(self, id, cmd):
    if not self.contains(id): return
    self.commands[id].append(cmd)
  
  def run_commands(self, id):
    yield from self.commands[id]
    self.commands[id].clear()
