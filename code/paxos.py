# -*- coding: utf-8 -*-

import os
import sys
import zmq
import random

myself = sys.argv[1]
peers = sys.argv[1:]
majority = len(peers) // 2 + 1
print("myself: {0}, peers: {1}, majority: {2}".format(myself, peers, majority))

def asbytes(obj):
    s = str(obj)
    if str is not bytes:
        # Python 3
        s = s.encode('ascii')
    return s

def read_proposal(fd):
    line = fd.readline()
    items = line.split()
    number = None
    value = None
    if len(items) == 2:
        number = int(items[0])
        value = int(items[1])
    elif len(items) == 1:
        number = int(items[0])
        value = None
    else:
        number = None
        value = None
    return (number, value)

def init(promised = "promised.txt", accepted = "accepted.txt"):
    fd1 = open(promised, "a+")
    fd1.seek(0)
    number1, value1 = read_proposal(fd1)

    fd2 = open(accepted, "a+")
    fd2.seek(0)
    number2, value2 = read_proposal(fd2)

    return (fd1, number1, fd2, number2, value2)

def remember_promised(fd, number):
    fd.seek(0)
    fd.truncate(0)
    fd.write("{0}".format(number))

def remember_accepted(fd, number, value):
    fd.seek(0)
    fd.truncate(0)
    if value:
        fd.write("{0} {1}".format(number, value))
    else:
        fd.write("{0}".format(number))

context = zmq.Context()

commander = context.socket(zmq.PULL)
commander.bind("ipc://commander-{0}.ipc".format(myself))

leader = context.socket(zmq.ROUTER)
identity = asbytes("leader-{0}".format(myself))
leader.setsockopt(zmq.IDENTITY, identity)
print("=== leader set identity to {0}".format(identity))

leader.bind("ipc://leader-{0}.ipc".format(myself))
print("=== leader listen on ipc://leader-{0}.ipc".format(myself))

acceptor = context.socket(zmq.ROUTER)
identity = asbytes("acceptor-{0}".format(myself))
acceptor.setsockopt(zmq.IDENTITY, identity)
print("=== acceptor set identity to {0}".format(identity))

poller = zmq.Poller()
poller.register(leader, zmq.POLLIN)
poller.register(acceptor, zmq.POLLIN)
poller.register(commander, zmq.POLLIN)

for peer in peers:
    print(">>> connecting ipc://{0}-leader.ipc".format(peer))
    acceptor.connect("ipc://leader-{0}.ipc".format(peer))

proposal_number = 0
saved_values = set()
self_value = random.randrange(1, 10000)

promised_proposal_number = None
promised_proposal_value = None

accepted_proposal_number = None
accepted_proposal_value = None

values = {}
choosed_value = None
leader_identity = None

self_leader = False

def make_promise(number):
    if accepted_proposal_number is None:
        return True
    if promised_proposal_number is None:
        return True
    return number > promised_proposal_number

promised_fd, promised_proposal_number, accepted_fd, accepted_proposal_number, accepted_proposal_value = init()
print("=== init: promised_fd({0}), promised_number({1}), accepted_fd({2}), accepted_number({3}), accepted_value({4})".format(promised_fd, promised_proposal_number, accepted_fd, accepted_proposal_number, accepted_proposal_value))

while True:
    socks = dict(poller.poll(timeout = 3000))
    if commander in socks:
        command = commander.recv()
        if command == b"LEADER":
            self_leader = True
            for peer in peers:
                identity = asbytes("acceptor-{0}".format(peer))
                leader.send_multipart([identity, b"LEADER"])
        else:
            print("===C leader: command({0}) not supported".format(command))

    elif leader in socks:
        msg = leader.recv_multipart()
        ident = msg[0]
        command = msg[1]
        print("###L recv: ident({0}), command({1})".format(ident, command))

        if command == b"PROPOSAL":
            value_s = msg[2]
            saved_values.add(value_s)
            print("###L recv: PROPOSAL({0})".format(msg))

            proposal_number += 1
            number_s = asbytes(str(proposal_number))
            values[number_s] = []

            for peer in peers:
                peer_ident = asbytes("acceptor-{0}".format(peer))
                print("###L send: ident({0}), PREPARE({1})".format(peer_ident, number_s))
                leader.send_multipart([peer_ident, b"PREPARE", number_s, value_s])

        elif command == b"PROMISE":
            proposal_n = msg[2]
            accepted_n = msg[3]
            accepted_v = msg[4]
            print("###L recv: ident({0}), PROMISE({1} -> {2} {3})".format(ident, proposal_n, accepted_n, accepted_v))

            if choosed_value is None:
                choosed_value = saved_values.pop()
                saved_values.add(choosed_value)

            # accepts: [(n1, v1), (n2, v2)]
            def choose_value(accepts):
                n1, v1 = None, None
                for n_s, v_s in accepts:
                    if n_s != b'' and v_s != b'':
                        n2 = int(n_s)
                        v2 = int(v_s)
                        if (n1 is not None) and (n2 > n1):
                            n1 = n2
                            v1 = v2
                return v1

            values[proposal_n].append((accepted_n, accepted_v))
            supports = len(values[proposal_n])
            print("###L supports: {0}, majority: {1}".format(supports, majority))
            if supports >= majority:
                accepted_value = choose_value(values[proposal_n])
                if accepted_value is None:
                    accepted_value = choosed_value
                for peer in peers:
                    peer_ident = asbytes("acceptor-{0}".format(peer))
                    leader.send_multipart([peer_ident, b"ACCEPT", proposal_n, accepted_value])

        elif command == b"LEARN":
            proposal_n = msg[2]
            accepted_value = msg[3]

            n = int(proposal_n)
            v = int(accepted_value)

            accepted_proposal_number = n
            accepted_proposal_value = v

            remember_accepted(accepted_fd, n, v)

    elif acceptor in socks:
        msg = acceptor.recv_multipart()
        ident = msg[0]
        command = msg[1]
        print("$$$A recv: ident({0}), command({1})".format(ident, command))

        if command == b"LEADER":
            value_s = asbytes(str(self_value))
            leader_identity = ident
            acceptor.send_multipart([ident, b"PROPOSAL", value_s])
            print("$$$A send: ident({0}), PROPOSAL({1})".format(ident, self_value))
        elif command == b"PREPARE":
            number_s = msg[2]
            print("$$$A recv: PREPARE({0})".format(number_s))

            success = make_promise(int(number_s))
            if success:
                promised_proposal_number = int(number_s)
                remember_promised(promised_fd, promised_proposal_number)

                n_s = b''
                if accepted_proposal_number and accepted_proposal_number < promised_proposal_number:
                    n_s = asbytes(str(accepted_proposal_number))

                v_s = b''
                if accepted_proposal_value:
                    v_s = asbytes(str(accepted_proposal_value))

                print("$$$A send: ident({0}), PROMISE({1} -> {2} {3})".format(ident, promised_proposal_number, n_s, v_s))
                acceptor.send_multipart([ident, b"PROMISE", number_s, n_s, v_s])
        elif command == b"ACCEPT":
            proposal_n = msg[2]
            accepted_value = msg[3]

            n = int(proposal_n)
            v = int(accepted_value)
            if n >= promised_proposal_number:
                accepted_proposal_number = n
                accepted_proposal_value = v
                remember_accepted(accepted_fd, n, v)
                acceptor.send_multipart([ident, b"LEARN", proposal_n, accepted_value])
                print("$$$A ACCEPT({0} {1})".format(proposal_n, accepted_value))
        elif command == b"DISCOVER":
            if leader_identity is None:
                leader_identity = ident

    else:
        # timeout

        # leader
        #print("###L self_leader: {0}".format(self_leader))
        if self_leader:
            for peer in peers:
                peer_ident = asbytes("acceptor-{0}".format(peer))
                #print("###L send: ident({0})".format(peer_ident))
                leader.send_multipart([peer_ident, b"DISCOVER"])

        # proposer
        #print("$$$P: accepted: {0}, leader_identity: {1}".format(accepted_proposal_value, leader_identity))
        if accepted_proposal_value is None and leader_identity:
            value_s = asbytes(str(self_value))
            #print("$$$P: send: ident({0}), PROPOSAL({1})".format(leader_identity, value_s))
            acceptor.send_multipart([leader_identity, b"PROPOSAL", value_s])
