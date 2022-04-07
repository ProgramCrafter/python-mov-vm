from registers import regs, IO_DEVICES
from utils import isint, byte

import time

def parse_int(v):
  try:
    w = int(v)
    return 0x8000 | (0x4000 if w < 0 else 0) | (abs(w) & 0x3FFF)
  except:
    return 0

def bytes_word(v):
  return b'%c%c' % (v // 256, v % 256)

registers_data = []
registers_cb = []
registers_id = {}

def create_r(name):
  if registers_id.get(name, None) == None:
    registers_id[name] = len(registers_data)
    registers_data.append(0)
    registers_cb.append(([], [])) # read, write
  
  return registers_id[name]

for callback in regs:
  triggers, args, results = [p.split('+') for p in callback.__doc__.lower().split('>')]
  
  loads = [create_r(a) for a in args]
  dumps = [create_r(a) for a in results]
  
  def create_proxy(trigger, loads=loads, dumps=dumps, callback=callback):
    def proxy():
      *results, = callback(trigger, *[registers_data[i] for i in loads])
      
      for i in range(len(dumps)):
        registers_data[dumps[i]] = results[i]
    return proxy
  
  for t in triggers:
    registers_cb[create_r(t[1:])][t[:1] == 'w'].append(create_proxy(t))

for reg in ('maddr addr reg0 reg1 reg2 reg3 reg4 reg5 reg6 reg7').split():
  create_r(reg)

print(registers_id)

def processor(raw_input, commands, limit=10000, debug=True):
  raw_commands = b''
  for c in commands:
    magic, src, dst = c.strip().lower().split(' ')
    
    if debug:
      print(len(raw_commands) // 4, magic, src, dst, sep='\t')
    
    raw_commands += bytes_word(parse_int(src) or registers_id[src]) + bytes_word(registers_id[dst])
  
  if debug:
    print(raw_commands, repr(raw_input))
    print()
  
  IO_DEVICES[0].buffer = raw_input
  IO_DEVICES[0].ptr = 0
  
  aid = create_r('addr')
  
  addr = 0
  for i in range(limit):
    if addr * 4 + 3 >= len(raw_commands): break
    
    src = raw_commands[addr * 4 + 0] * 256 + raw_commands[addr * 4 + 1]
    dst = raw_commands[addr * 4 + 2] * 256 + raw_commands[addr * 4 + 3]
    
    if not (src & 0x8000):
      # executing read callbacks
      for c in registers_cb[src][0]: c()
      
      src = registers_data[src]
    else:
      # converting number
      src = (src & 0x3FFF) * (-1 if (src & 0x4000) else 1)
    
    registers_data[aid] = addr + 1
    registers_data[dst] = src
    for c in registers_cb[dst][1]: c()
    addr = registers_data[aid]
  
  # time.sleep(10)
  regs[5]('wcio', 257) # resetting CURSES
  
  return i
