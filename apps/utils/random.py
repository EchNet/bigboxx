import time


class KISSGenerator:
  """
    Class KISSGenerator implements the KISS random number generator
    developed by George Marsaglia at Florida State University through
    research supported by NSF Grant DMS-9206972.
    @author Rex Carlson mathmanrex@hotmail.com
  """
  seed_w = 0
  seed_x = 0
  seed_y = 0
  seed_z = 0

  def __init__(self, seed=None):
    """
      Seed is one of:
        None, in which case the current time is used to seed the generator;
        A long integer, which is used to seed the generator;
        A tuple of size 4, which is the initial generator state.
    """
    if seed is None:
      self.seed(int(round(time.time() * 1000)))
    elif isinstance(seed, int):
      self.seed(seed)
    elif isinstance(seed, tuple) and len(seed) == 4:
      self.seed_w = seed[0]
      self.seed_x = seed[1]
      self.seed_y = seed[2]
      self.seed_z = seed[3]
    else:
      raise TypeError()

  def seed(self, seed):
    """
      Reset the sequence of this random number generator based on a single 
      long integer.
    """
    self.seed_w = 916191069  # DO NOT CHANGE THIS VALUE !!!
    self.seed_x = (seed >> 32) & 0xffffffff
    self.seed_y = (seed | 1) & 0xffffffff  # May not be zero.
    self.seed_z = 521288629  # DO NOT CHANGE THIS VALUE !!!

  def getstate(self):
    return (self.seed_w, self.seed_x, self.seed_y, self.seed_z)

  def getrandbits(self, nbits):
    rand = self.getrand32bits()
    if nbits <= 32:
      return rand >> (32 - nbits)
    else:
      return (rand << (nbits - 32)) + self.getrandbits(nbits - 32)

  def getrand32bits(self):
    # LC generator - not full period - loop defined by initial seed_w
    self.seed_w = 30903 * (self.seed_w & 0xffff) + (self.seed_w >> 16)

    # LC generator - period = 2^32
    self.seed_x = (69069 * self.seed_x + 1327217885) & 0xffffffff

    # LFSR generator - period = 2^32-1 (Zero not allowed)
    self.seed_y ^= (self.seed_y << 13)
    self.seed_y ^= (self.seed_y >> 17)
    self.seed_y ^= (self.seed_y << 5)
    self.seed_y &= 0xffffffff
    # GENERATE FAULT ON ZERO VALUE
    if self.seed_y == 0:
      raise ValueError()

    # LC generator - not full period - loop defined by initial seed_z
    self.seed_z = 18000 * (self.seed_z & 0xffff) + (self.seed_z >> 16)

    return ((self.seed_w << 16) + self.seed_x + self.seed_y + (self.seed_z & 0xffff)) & 0xffffffff
