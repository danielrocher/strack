#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import subprocess, re, sys
from threading import Thread

class StraceProcess(Thread):
    def __init__(self, pid=None, program=None, syscalls="", callback=None):
        Thread.__init__(self)
        self.filename=program
        self.syscalls=syscalls
        self.process=None
        self.callback=callback
        self.running=False

    def stdout(self, msg):
        self.callback(msg)

    def run(self):
        if self.process :
            return
        try:
            with open(self.filename) as f:
                for line in f.readlines():
                    self.stdout(line.replace('\n', ''))
        except IOError:
            print "Impossible to read file"
            self.process=None
            self.running=False

    def isRunning(self):
        return self.running

    def stop(self):
        if self.process==None :
            return
        self.process.kill()
        self.process=None
        self.running=False


if __name__ == '__main__':
    def callback(msg):
        print msg

    syscalls="execve,open,socket,connect,accept,sendto,recvfrom,sendmsg,recvmsg,bind,listen,socketpair,accept4,recvmmsg,sendmmsg"
    thread = StraceProcess(program="../utest/test_strace.txt", syscalls=syscalls, callback=callback)
    thread.start()



