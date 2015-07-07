#==============================================================================#
#                                optionmenu.py                                 #
#==============================================================================#

#============#
#  Includes  #
#============#

import sys
import re
import vim

from messagebox import MessageBox
from statusline import StatusLine
from processbox import ProcessBox

#========#
#  Misc  #
#========#

MISSING_BUFFER = "Cannot find eZ's target buffer (%s)"
MISSING_WINDOW = "Cannot find window (%s) for eZ's target buffer (%s)"

#===========#
#  Methods  #
#===========#

def check_sanity():
  """ Make sure that the target buffer still exists """

  b = int(vim.eval('g:ez_target_n'))

  if not vim.eval('bufloaded(%d)' % b):
      vim.command('echo "%s"' % (MISSING_BUFFER % b))
      return False

  w = int(vim.eval('bufwinnr(%d)' % b))
  if w == -1:
      vim.command('echo "%s"' % (MISSING_WINDOW % (w, b)))
      return False

  return True

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

def initPythonModule():
    if sys.version_info[:2] < (2, 4):
        vim.command('let s:has_supported_python = 0')

def eZRender():
  """ Renders the currently selected menu buffer """
  if not check_sanity():
    return

  goto_window_for_buffer_name('__ez_options__')

  menu = eZMenu.get_selected()
  if hasattr(menu, 'header'):
    header = menu.header
  else:
    header = []

  vim.command('setlocal modifiable')
  result = menu.get_items()
  vim.current.buffer[:] = header + result
  vim.command('setlocal nomodifiable')

  menu.set_cursor()

def eZExecuteOption():
  if not check_sanity():
    return

  state = eZMenu.get_state()
  menu = eZMenu.get_selected()
  if state in menu.callbacks:
    menu.callbacks[state]()

def open_statusline():
  StatusLine.open()

def connect_func():
  import ez_client as cl
  import os
  cl.cl.cmd_authenticate(os.environ["ez_host"], int(os.environ["ez_port"]))

#==============================================================================#
#                                    eZMenu                                    #
#==============================================================================#

class eZMenu(object):
  """ Simple menu implementation in vim. Enables generic items and callbacks.
  """
  # stores the selected menu s in the order they were invoked. The last one,
  # i.e. selected[-1] is the active one.
  selected = []

  nmenu = 0  # number of menus
  registry = {}  # provides global access to the indivial menu with the
                 # knowledge of the menu id
  id_by_name = {}  # menu name -> menu id
  empty_line = '|'  # symbol used to separate items

  def __init__(self, name=None, header=None, quit_rule=None):
    eZMenu.nmenu += 1
    if header:
      self.header = header
    if quit_rule:
      self.quit_rule = quit_rule

    if name:
      eZMenu.id_by_name[name] = eZMenu.nmenu

    self.registry[eZMenu.nmenu] = self
    self.items = {}
    self.storage = {}
    self.callbacks = {}

    if header:
      self.zero_cursor_pos = len(self.header) + 1
    else:
      self.zero_cursor_pos = 1

    self.cursor_pos = self.zero_cursor_pos

  def add_item(self, item, callback=None, storage=None):
    """ Add a menu item """
    index = len(self.items) + 1
    self.items[index] = '- [' + str(index) + '] ' + item
    if callback:
      self.callbacks[index] = callback
    if storage:
      self.storage[index] = storage

  def clear_item(self, item):
    found = [index for index, item_t in self.items.iteritems()
             if item in item_t]
    if len(found) == 1:
      index = found[0]
      del self.items[index]
      if index in self.callbacks:
        del self.callbacks[index]
      if index in self.storage:
        del self.storage[index]
    else:
      raise Exception('Item could not be (uniquely) identified.')

  def clear_items(self):
    self.items = {}
    self.callbacks = {}
    self.cursor_pos = self.zero_cursor_pos

  def get_items(self):
    """ Return menu items """
    lst = []
    if len(self.items) == 0:
      return []
    for u in range(1, len(self.items)):
      lst.append(self.items[u])
      lst.append(self.empty_line)
    lst.append(self.items[len(self.items)])
    return lst

  def set_cursor(self):
    """ Sets the cursor at the the postion `self.cursor_pos` """
    pos = self.cursor_pos
    vim.command('call cursor(' + str(pos) + ', 0)')

  def move_cursor_menu(self, dir):
    """ Moves the cursor in the direction `dir`. """
    dist = 2
    target_line = vim.current.line
    if '[' not in target_line:
      dist = 1
    win = vim.current.window
    pos = win.cursor[0]

    newpos = pos + dir*dist
    if newpos < self.zero_cursor_pos:
      newpos = self.zero_cursor_pos

    self.cursor_pos = newpos
    self.set_cursor()

  @classmethod
  def get_selected(self):
    """ Returns which menu is currently selected """
    if self.selected[-1] in self.registry:
      return self.registry[self.selected[-1]]
    else:
      raise Exception('Selected menu ' + str(self.selected) + ' does not exist')

  @staticmethod
  def get_state(line=None):
    """ Returns which menu item is currently selected. """
    if line:
      target_line = line
    else:
      target_line = vim.current.line

    res = re.search('\[(\d+)\]', target_line)
    if res is not None:
      return int(res.groups()[0])
    else:
      raise Exception('Coud not `get_state` the line: ' + str(target_line))

  @staticmethod
  def get_item(line=None):
    """ Returns the currently selected line. """
    if line:
      target_line = line
    else:
      target_line = vim.current.line

    res = re.search('\[(\d+)\](.*)', target_line)
    if res is not None:
      groups = res.groups()
      state = int(groups[0])
      line = groups[1]
      return state, line
    else:
      raise Exception('Coud not `get_item` the line: ' + str(target_line))

  def update_item(self, state, item, callback=None, storage=None):
    current_item = self.items[state]
    if item != current_item:
      self.items[state] = '- [' + str(state) + '] ' + item
      eZRender()
    if callback:
      self.callbacks[state] = callback
    if storage:
      self.storage[state] = storage

  @classmethod
  def move_cursor(cls):
    """ Moves the cursor in the direction specified in buffer variable
    `b:direction` for the currerntly selected menu. """
    menu = cls.get_selected()
    dir = int(vim.eval('b:direction'))
    menu.move_cursor_menu(dir)

  @classmethod
  def close_menu(cls):
    """ Close eZMenu buffer. """
    if goto_window_for_buffer_name('__ez_options__'):
      # close current window, i.e. __eZchat_Preview__
      vim.command('quit')
      # return to the window from which the menu was opened
      vim.command('exe bufwinnr(g:ez_target_n) . "wincmd w"')

  @classmethod
  def menu_move_up(cls, ignore_quitrule=False):
    """ Moves to the previous menu. The main menu is closed by invoking
    menu_move_up. """
    menu = cls.get_selected()
    if ignore_quitrule or not hasattr(menu, 'quit_rule'):
      if len(cls.selected) == 1:
        cls.close_menu()
      else:
        cls.selected.pop(-1)
        eZRender()
    else:
      menu.quit_rule()

  @classmethod
  def set_selected(cls, menuid):
    """ Set which menu is rendered when eZRender is invoked.

    :menuid: either menu id as int or name
    """
    if type(menuid) is int:
      idd = menuid
    elif type(menuid) is str:
      if menuid not in cls.id_by_name:
        raise Exception('Menuid ' + str(menuid) + ' not registered.')
      idd = cls.id_by_name[menuid]

    if idd not in cls.registry:
      raise Exception('Menuid ' + str(idd) + ' not registered.')

    cls.selected.append(idd)

  @classmethod
  def change_menu(cls, menuid):
    cls.set_selected(menuid)
    eZRender()


#=============#
#  Main Menu  #
#=============#

main_mappings = (vim.eval('g:ez_map_move_older'),
                 vim.eval('g:ez_map_move_newer'))

ezintro = '''\
" Welcome to eZchat.
" %s/%s  - move between options
" <cr> - select option

'''
main_header = (ezintro % main_mappings).splitlines()

mainmenu = eZMenu(name='main', header=main_header)

mainmenu.add_item('Connect', callback=connect_func)

def open_menu(menuid):
  def eval_cmd():
    if menuid == 'contacts':
      gen_contactsmenu(contactmenu)
    elif menuid == 'processes':
      gen_processmenu(processmenu)
    return eZMenu.change_menu(menuid)
  return eval_cmd

mainmenu.add_item('Contacts', callback=open_menu('contacts'))
mainmenu.add_item('Processes', callback=open_menu('processes'))
mainmenu.add_item('Preferences')
mainmenu.add_item('Status messages', callback=open_statusline)
eZMenu.set_selected('main')

#=================#
#  Contacts Menu  #
#=================#

def contact_quitrule():
  """ Triggers what happens when contacts is `closed`. If the user has selected
  contacts the message box is opened with a new chat session with all the
  selected contacts. """
  selected = []
  for state, item in contactmenu.items.iteritems():
    if '[x]' in item:
      selected.append(state)
  if len(selected) > 0:
    eZMenu.menu_move_up(ignore_quitrule=True)
    # session = tuples of fingerprints
    session = tuple(contactmenu.storage[u] for u in selected)
    MessageBox.open_message_box()
    MessageBox.switch_session(session)
  else:
    eZMenu.menu_move_up(ignore_quitrule=True)

contactmenu = eZMenu(name='contacts', quit_rule=contact_quitrule)

def gen_contactsmenu(contactmenu):
  """ Generates the contacts menu. """

  contactmenu.clear_items()
  contacts = MessageBox.contact_list()
  for contact in contacts:
    status = contact['status']
    user_id = contact['user_id']
    fingerprint = contact['fingerprint']
    not_marked = '[ ]'
    button_label = user_id + ' ' + status + ' ' + not_marked

    # pressing <CR> toggles if the contact is selected ([x]) or not ([ ])
    def contact_callback(user_id, status):
      def mark_contact():
        state, line = eZMenu.get_item()
        if '[x]' in line:
          new_button_label = user_id + ' ' + status + ' [ ]'
        else:
          new_button_label = user_id + ' ' + status + ' [x]'
        contactmenu.update_item(state, new_button_label)
      return mark_contact

    contactmenu.add_item(button_label,
                         callback=contact_callback(user_id, status),
                         storage=fingerprint)


#================#
#  Process Menu  #
#================#

processmenu = eZMenu(name='processes')

def gen_processmenu(processmenu):
  """ Generates the process menu. """

  processmenu.clear_items()
  processes = ProcessBox.process_list()
  vim.command('echo "process numbers' + str(len(processes)) + '"')
  for process in processes:
    status = process['status']
    pr_id = process['id']
    pr_label = str(pr_id) + ' ' + status
    kill_cll = process['kill_callback']

    def kill_render():
      kill_cll()
      processmenu.clear_item(pr_label)
      eZRender()

    processmenu.add_item(pr_label,
                         callback=kill_render)
