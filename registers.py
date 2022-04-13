from devices import IO_DEVICES

import curses
import time
import os

memory = [b'']

def add(trig, reg0, reg1):
  'wadd0+wadd1>add0+add1>add'
  return reg0 + reg1,

def sub(trig, reg0, reg1):
  'wsub0+wsub1>sub0+sub1>sub'
  return reg0 - reg1,

def mul(trig, reg0, reg1):
  'wmul0+wmul1>mul0+mul1>mul'
  return reg0 * reg1,

def div(trig, reg0, reg1):
  'wdiv0+wdiv1>div0+div1>div+mod'
  if reg1 == 0: return reg0, 0
  return reg0 // reg1, reg0 % reg1

def tlt(trig, reg0, reg1):
  'wtlt0+wtlt1>tlt0+tlt1>tlt'
  return int(reg0 < reg1),

screen = curses.initscr()
curses.def_shell_mode()
screen.nodelay(True)
curses.cbreak()
curses.noecho()

def curses_io(trig, reg0):
  'wcio+rcio>cio>cio'
  
  if trig == 'wcio':
    if reg0 == 256:
      screen.refresh()
      curses.napms(50)
      screen.clear()
    elif reg0 == 257:
      curses.reset_shell_mode()
    else:
      if reg0 > 257:
        print('Warning: trying to output', reg0)
      screen.addch(reg0)
    return 0,
  else:
    return screen.getch(),

def io(trig, reg0, reg1):
  'wio1+rio>io0+io1>io'
  if reg0 >= len(IO_DEVICES):
    return 0,
  
  if trig == 'wio1':
    if reg0 == 0:
      print(end=chr(reg1 % 256))
    else:
      IO_DEVICES[reg0].write(1, chr(reg1 % 256))
    return 0,
  else:
    return ord(IO_DEVICES[reg0].read(1) or '\x00'),

def atz(trig, atz0, atz1, atz2):
  'watz0+watz1+watz2>atz0+atz1+atz2>atz'
  
  if atz0 == 0: return atz1,
  return atz2,

def _legacy(trig, _, __): # empty register between memory and maddr
  '>memory+>'
  return tuple()

def mem(trig, value, maddr):
  'wmemory+rmemory>memory+maddr>memory'
  
  if trig == 'wmemory':
    memory[0] = memory[0][:maddr*8] + value.to_bytes(8, 'big') + memory[0][maddr*8+8:]
    return value,
  else:
    return int.from_bytes(memory[0][maddr*8:maddr*8+8], 'big'),

def log(trig, value):
  'wlog>log>'
  print('>', value, chr(value % 256))
  return 0,

def qlog(trig, value):
  'wqlog>qlog>'
  print(chr(value % 256), end='')
  return 0,

regs = [add, sub, mul, div, tlt, curses_io, io, atz, _legacy, mem, log, qlog]
