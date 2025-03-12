# -*- coding: utf-8 -*-

import sys
import zmq

def usage():
    print("usage: {0} <leader>")
    sys.exit(1)

if len(sys.argv) != 2:
    usage()

where = sys.argv[1]

context = zmq.Context()
commander = context.socket(zmq.PUSH)
commander.connect("ipc://commander-{0}.ipc".format(where))

commander.send(b"LEADER")
