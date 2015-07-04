#==============================================================================#
#                                   relay.py                                   #
#==============================================================================#

#============#
#  Includes  #
#============#

import sys
import types
import os
import signal
import subprocess
import select
import vim
from time import sleep

from ez_process import p2pReply, p2pCommand

import ez_preferences as ep
import ez_client as cl
import fcntl

from statusline import StatusLine
from messagebox import MessageBox

#===========#
#  Methods  #
#===========#

def status_update(msg):
  StatusLine.append(msg)

def msg_update(msg, fingerprint):
  session = (fingerprint, )
  MessageBox.append_session(session, msg)

def received_output(data):
  categories = {p2pReply.success: 'success',
                p2pReply.error: 'error',
                p2pReply.msg: 'msg'}

  vim.command('echo "' + str(data) + '"')
  if 'status' in data.strip():
    try:
      reply = cl.cl.replyQueue.get(block=False)
    except:
      reply = None
    while reply:
      if((reply.replyType == p2pReply.success) or
         (reply.replyType == p2pReply.error)):
        status = ("success" if reply.replyType == p2pReply.success
                  else "ERROR")
        status_update(('Client reply %s: %s' % (status, reply.data)))
      elif reply.replyType == p2pReply.msg:
        # decrypt msg and print it on the screen
        if reply.data.recipient == cl.cl.fingerprint:
          try:
            msg_dct = reply.data.clear_message()
            # if target is set and the recipient is the user himself the
            # message is put to the target
            if(reply.data.target is not None and
               reply.data.recipient == cl.cl.fingerprint):
              sender = reply.data.target
            else:
              sender = reply.data.sender

            # try to reconstruct the username given the fingerprint
            sender_name = cl.cl.get_user(msg_dct['sender'])
            if not sender_name:
              sender_name = msg_dct['sender']

            sender_str = ' '.join([sender_name, "@",
                                   msg_dct['time'], ":\n"])

            msg_str = msg_dct['content']
            msg_update(sender_str + msg_str, sender)
          except Exception, e:
            status_update("Error: %s" % str(e))

      else:
        # this case should not happen! (if theres something in the queue it
        # must be success,error or msg)
        status_update('Client sent unknown status.')
      try:
        reply = cl.cl.replyQueue.get(block=False)
      except:
        reply = None
  else:
    # this case should not happen! (if theres something in the queue, it
    # must be success,error or msg)
    status_update('Client sent unknown status.')
  return True


def eZResponse():
  rval = received_output('status')

def eZShutdown():
  cl.cl.enqueue('shutdown')

def event_callback():
  import thread
  suppress_error = False
  if suppress_error:
    cmd = "vim --servername ez --remote-expr 'EZResponseCll()' >/dev/null 2>$1"
  else:
    cmd = "vim --servername ez --remote-expr 'EZResponseCll()' >/dev/null"
  import threading
  thread.start_new_thread(os.system, (cmd,))
  from time import sleep
  sleep(0.1)

#===============#
#  Init client  #
#===============#

if __name__ == "__main__":
  ep.init_cli_preferences()
  sn = vim.eval('v:servername')
  if sn != 'EZ':
    status_update('Vim was not started in servermode. ' +
                  'Start vim with `vim --servername ez` ' +
                  'if auto event callback should be enabled.')
    cl.init_client('jlang', write_to_pipe=False, **ep.process_preferences)
  else:
    cl.init_client('YOURNAME', write_to_pipe=False, event_callback=event_callback,
                   **ep.process_preferences)
