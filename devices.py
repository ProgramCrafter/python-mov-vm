class Terminal:
  def __init__(self):
    self.clear()
  
  def read(self, size):
    self.ptr += size
    return self.buffer[self.ptr-size:self.ptr]
  
  def clear(self):
    self.buffer = ''
    self.ptr = 0

IO_DEVICES = [Terminal()]