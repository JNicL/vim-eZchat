#==============================================================================#
#                                statusline.py                                 #
#==============================================================================#

#============#
#  Includes  #
#============#

import vim

#==============================================================================#
#                                  StatusLine                                  #
#==============================================================================#

class StatusLine(object):
  ez_statusline_buffer = '__ez_statusline_buffer__'

  @classmethod
  def buffer_exists(cls):
    vim.command('let s:existing_statusline_buffer = bufnr("' +
                cls.ez_statusline_buffer + '")')
    cls.nstatusline = int(vim.eval('s:existing_statusline_buffer'))
    # statusline does not exist
    if cls.nstatusline == -1:
      return False
    else:
      return True

  @classmethod
  def create(cls):
    if not cls.buffer_exists():
      ww = vim.current.window
      vim.command('exe "botright new ' + cls.ez_statusline_buffer + '"')
      cls.resize()
      vim.current.window = ww

  @classmethod
  def open(cls):
    if cls.buffer_exists():
      w = int(vim.eval('bufwinnr(%d)' % cls.nstatusline))
      if w == -1:
        # window must be created
        ww = vim.current.window
        vim.command('exe "botright split ' +
                    cls.ez_statusline_buffer + '"')
        cls.resize()
        vim.current.window = ww
    else:
      ww = vim.current.window
      vim.command('exe "botright new ' + cls.ez_statusline_buffer + '"')
      cls.resize()
      vim.current.window = ww

  @classmethod
  def opened(cls):
    w = int(vim.eval('bufwinnr(%d)' % cls.nstatusline))
    if w == -1:
      return False
    else:
      return True

  @classmethod
  def resize(cls):
    vim.command('exe "resize " . g:ez_statusline_height')

  @classmethod
  def close(cls):
    if cls.buffer_exists():
      wn = int(vim.eval('bufwinnr(%d)' % cls.nstatusline))
      ww = vim.current.window
      vim.command('%dwincmd w' % wn)
      if ww.number == wn:
        vim.command('quit')
      else:
        vim.command('quit')
        vim.current.window = ww

  @classmethod
  def append(cls, msg):
    cls.create()
    assert(cls.buffer_exists())
    buf = vim.buffers[cls.nstatusline]
    buf.options['modifiable'] = True
    buf[:] = [msg] + buf[:]
    buf.options['modifiable'] = False
