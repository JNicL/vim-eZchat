#==============================================================================#
#                                messagebox.py                                 #
#==============================================================================#

#============#
#  Includes  #
#============#

import vim
import re
import ez_client as cl

#===========#
#  Methods  #
#===========#

def goto_window_for_buffer(b):
    w = int(vim.eval('bufwinnr(%d)' % int(b)))
    if w != -1:
      vim.command('%dwincmd w' % w)
      return True
    else:
      return False

def goto_window_for_buffer_name(bn):
    b = vim.eval('bufnr("%s")' % bn)
    return goto_window_for_buffer(b)


#==============================================================================#
#                                  MessageBox                                  #
#==============================================================================#

class MessageBox(object):
  """ Handles writing messages and provides a message box for displaying
  received messages. """

  ez_message_buffer = '__ez_message_buffer__'
  ez_write_buffer = '__ez_write_buffer__'

  sessions = 0
  selected = None
  registry = {}
  id_by_name = {}

  def __init__(self, args):
    MessageBox.sessions += 1
    session_id = MessageBox.sessions
    self.name = args
    self.id_by_name[self.name] = session_id
    self.registry[session_id] = self
    self.buffer = []

  @classmethod
  def message_box_opened(cls):
    """ Returns true if the message box is opened, else False """

    # Search in all opened tabs
    vim.command('redir => s:tabs|silent tabs|redir END')
    tabs = (vim.eval('s:tabs'))
    pt = ParseTabs(tabs)

    # keep the result globally available
    cls.pt = pt

    tabn1 = pt.get_tabs_from_buffer(cls.ez_message_buffer)
    tabn2 = pt.get_tabs_from_buffer(cls.ez_write_buffer)
    if tabn1 != tabn2:
      raise Exception('Messed up message box.' + str(pt.tabs))

    if tabn1:
      return True
    else:
      return False

  @classmethod
  def open_message_box(cls):
    if not cls.message_box_opened():
      vim.command('let b:target_tabpage = tabpagenr()')
      cls.last_tabpage_target = vim.eval('b:target_tabpage')
      cls.last_buffer_target = vim.current.buffer.name
      vim.command('tabnew ' + cls.ez_write_buffer)
      vim.command('split ' + cls.ez_message_buffer)
      goto_window_for_buffer_name(cls.ez_write_buffer)
    else:
      buffer_target = vim.current.buffer.name
      if(buffer_target != cls.ez_write_buffer and
         buffer_target != cls.ez_message_buffer):
        tabn = cls.pt.get_tabs_from_buffer(cls.ez_message_buffer)
        tabn = tabn[0]
        vim.command('tabn ' + str(tabn))
        goto_window_for_buffer_name(cls.ez_write_buffer)

  @classmethod
  def close_message_box(cls):
    if cls.message_box_opened():
      buffer_target = vim.current.buffer.name
      if(buffer_target != cls.ez_write_buffer and
         buffer_target != cls.ez_message_buffer):
        tabn = cls.pt.get_tabs_from_buffer(cls.ez_message_buffer)
        if len(tabn) != 1:
          raise Exception('Multiple message buffers present!')
        vim.command('tabn ' + str(tabn[0]))
      vim.command('tabclose')

  @classmethod
  def get_message_buffer(cls):
    vim.command('let b:message_buffer = bufnr("' + cls.ez_message_buffer + '")')
    bufn = int(vim.eval('b:message_buffer'))
    buf = vim.buffers[bufn]
    return buf

  @classmethod
  def get_write_buffer(cls):
    vim.command('let b:write_buffer = bufnr("' + cls.ez_write_buffer + '")')
    bufn = int(vim.eval('b:write_buffer'))
    buf = vim.buffers[bufn]
    return buf

  @classmethod
  def fill_message_buffer(cls):
    """ Writes the messages stored in the currently selected session to the
    message buffer (render in vim). """

    if cls.selected is not None:
      buf = cls.get_message_buffer()
      buf.options['modifiable'] = True
      buf[:] = cls.registry[cls.selected].buffer
      buf.options['modifiable'] = False
    else:
      buf = cls.get_message_buffer()
      buf.options['modifiable'] = True
      buf[:] = ['Hi there,', 'this is a test']
      buf.options['modifiable'] = False

  @classmethod
  def append_message_buffer(cls, content):
    """ Appends content to the message buffer. """
    buf = cls.get_message_buffer()
    buf.options['modifiable'] = True
    buf.append(content)
    buf.options['modifiable'] = False
    cls.scroll_message_bottom()

  @classmethod
  def append_session(cls, session, msg):
    """ Appends msg to the session `session`. """
    msg = msg.split('\n')
    if session not in cls.id_by_name:
      cls(session)
    session_id = cls.id_by_name[session]
    if session_id == cls.selected:
      cls.append_message_buffer(msg)
    cls.registry[session_id].buffer.append(msg)

  @classmethod
  def scroll_message_bottom(cls):
    win_cur = vim.current.window
    goto_window_for_buffer_name(cls.ez_message_buffer)
    vim.command('normal G')
    vim.current.window = win_cur

  @classmethod
  def clear_buffer(cls, buf):
    if not buf.options['modifiable']:
      buf.options['modifiable'] = True
      buf[:] = None
      buf.options['modifiable'] = False
    else:
      buf[:] = None

  @classmethod
  def send_message(cls):
    """ Forwards the write_buffer content to `process_message`. """
    buf = cls.get_write_buffer()
    content = buf[:]
    cls.clear_buffer(buf)
    cls.process_message(content)

  @classmethod
  def process_message(cls, msg):
    """ Stores the msg in the currently selected session and sends the msg via
    eZchat. The recipient(s) is(are) determined from the session name. """
    if type(msg) is list:
      cls.registry[cls.selected].buffer.extend(msg)
    else:
      cls.registry[cls.selected].buffer.append(msg)

    fingerprints = cls.registry[cls.selected].name
    for fingerprint in fingerprints:
      cl.cl.cmd_send_msg(msg, fingerprint=fingerprint)

  @classmethod
  def switch_session(cls, session, new=True):
    """ Switch to the session `session`. If not existent the session is
    created."""
    #if len(args) == 1 and args[0] is int:
      #cls.selected = args[0]
      #cls.fill_message_buffer()
    #else:
    if session in cls.id_by_name:
      cls.selected = cls.id_by_name[session]
      cls.fill_message_buffer()
    elif new:
      cls(session)
      cls.switch_session(session, new=new)

  @classmethod
  def contact_list(cls):
    """ Retreives the contacts list from the eZchat """
    UIDs = cl.cl.UserDatabase.UID_list()
    if len(UIDs) > 0:
      contacts = [(str(entry.name), entry.UID) for entry in
                  cl.cl.UserDatabase.get_entries(UIDs) if not cl.cl.name ==
                  entry.name]
    else:
      contacts = []

    # construct user/online list
    if len(contacts) > 0:
      # online users identified by fingerprint not user_id
      users_online = [u[1] for u in cl.cl.ips.values()]
      contacts = [(contact, contact[1] in users_online) for contact in contacts]

    online_users = cl.cl.ips.values()
    contact_states = []
    for user_fingerprint, status in contacts:
      user_id, fingerprint = user_fingerprint
      status = 'ON' if status else 'OFF'

      user = {'user_id': user_id, 'fingerprint': fingerprint, 'status': status}

      contact_states.append(user)
    cls.contact_stats = contact_states
    return cls.contact_stats

#==============================================================================#
#                                  ParseTabs                                   #
#==============================================================================#

class ParseTabs(object):
  """ Parses vim's command `tabs`.

  >>> t1 = "Tab page 1\n    buff1\n    buff2\n> + buff3\n"
  >>> t2 = "Tab page 2\n    buff4\n    buff2\n    buff6\n"
  >>> tabstest = t1+t2
  >>> pt = ParseTabs(tabstest)
  >>> pt.get_tabs_from_buffer('buff1')
  [1]
  >>> pt.get_tabs_from_buffer('buff1')
  [1, 2]
  >>> pt.get_tabs_from_buffer('buff7')
  None
  """
  # general tabs pattern. first group stores the tab number, the second group
  # stores all the lines after `Tab page \d+` pattern.
  tabpat = r'Tab page (\d+)\s(.+?)(?=$(?!\n)|(?=Tab page))'
  tabpat = re.compile(tabpat, re.MULTILINE | re.DOTALL)

  def __init__(self, tabs):
    self.tabs = {}
    for tab in self.tabpat.findall(tabs + '\n'):
      tabn = int(tab[0])
      windows = tab[1].split('\n')
      del windows[-1]
      wins = {}
      for window in windows:
        # first char is reserved for >
        selected = window[0] == '>'
        # dont know if reserved
        assert(window[1] == ' ')
        # third char is reserved for +
        edited = window[2] == '+'
        # dont know if reserved
        assert(window[3] == ' ')
        # buffername 4:end
        win = window[4:]

        win_prop = {'buffer': win, 'selected': selected, 'edited': edited}
        wins[win] = win_prop

      self.tabs[tabn] = wins

  def __repr__(self):
    return str(self.tabs)

  def get_tabs_from_buffer(self, buff):
    """ Returns the tabnumber which displayes the buffer `buff`. """
    ret = []
    for tabn in self.tabs:
      if buff in self.tabs[tabn]:
        ret.append(tabn)
    if ret != []:
      return ret
