#==============================================================================#
#                                processbox.py                                 #
#==============================================================================#

#============#
#  Includes  #
#============#

import vim
import ez_client as cl

class ProcessBox(object):
  """ Handles running processes and provides a methods for starting, pausing and
  aborting processes."""

  @classmethod
  def process_list(cls):
    """ Retreives the process list from the eZchat. """
    processes = cl.cl.background_processes
    pr_list = []

    def close_process(process_id):
      def eval_cmd(*args):
        cl.cl.cmd_stop_background_process(process_id)
      return eval_cmd

    for process_id in processes:
      pr = processes[process_id]
      pr_on = not pr.finished.isSet()
      status = 'ON' if pr_on else 'OFF'

      pr_dict = {'id': process_id, 'status': status,
                 'kill_callback': close_process(process_id)}
      pr_list.append(pr_dict)

    return pr_list
