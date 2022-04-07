from movemu_lib import processor

import sys

def preprocess(asm):
  marks = {}
  variables = []
  
  commands = []
  for line in asm.split('\n'):
    if not line: continue
    
    line += ' '
    line = line[:line.find('--')]
    
    if not line.startswith(' '):
      if ' ' in line.strip():
        mark, operation = line.split(' ', 1)
      else:
        mark, operation = line.strip(), ''
    else:
      mark, operation = '', line.strip()
    
    if mark:
      marks[mark] = len(commands)
    
    if operation:
      magic, source, dest = operation.split(' ')
      
      if source.startswith('[') and source.endswith(']'):
        # allocating variable
        if source not in variables:
          variables.append(source)
      if dest.startswith('[') and dest.endswith(']'):
        # allocating variable
        if dest not in variables:
          variables.append(dest)
      
      commands.append((magic, source, dest))
  
  for (magic, source, dest) in commands:
    if source.startswith('$'):
      source_mark = source[1:]
      if source_mark in marks:
        source = str(marks[source_mark])
    elif source.startswith('[') and source.endswith(']'):
      variable_index = variables.index(source)
      source = 'reg%d' % variable_index
    
    if dest.startswith('[') and dest.endswith(']'):
      variable_index = variables.index(dest)
      dest = 'reg%d' % variable_index
    
    yield '%s %s %s' % (magic, source, dest)

if __name__ == '__main__':
  file = __file__ + '/../code.movasm' if len(sys.argv) < 2 else sys.argv[1]
  with open(file) as f:
    input_data = f.readline()
    data = f.read()
  
  ldata = len(data) + 1
  while len(data) < ldata:
    ldata = len(data)
    data = data.replace('  ', ' ')
  
  print('\nExecuting...\n')
  print(processor(input_data, preprocess(data), limit=10**7))
  
  input()
