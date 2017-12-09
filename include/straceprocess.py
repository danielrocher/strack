#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import subprocess, re, sys
from threading import Thread

class StraceProcess(Thread):
    def __init__(self, pid, syscalls, callback=None):
        Thread.__init__(self)
        self.pid=pid
        self.syscalls=syscalls
        self.process=None
        self.callback=callback
        self.running=False

    def stdout(self, msg):
        self.callback(msg)

    def run(self):
        if self.process :
            return
        self.pid=re.sub("\s+", " ", self.pid).split(' ')
        for x in self.pid:
            try:
                x=int(x)
                continue
            except:
                print "Pid must be a number."
                return

        self.pid=",".join(self.pid)
        try:
            self.process = subprocess.Popen(["strace", "-f", "-q", "-p", self.pid, "-e", self.syscalls, "-y" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.running=True
            for line in iter(self.process.stdout.readline, ''):
                self.stdout(line.replace('\n', ''))
                if self.process==None :
                    self.running=False
                    return

        except OSError:
            print "Failed to use strace."
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
    import signal, time
    global thread

    def callback(msg):
        print msg

    def signal_handler(signal, frame):
        print "Wait. Stopping all ..."
        global thread
        thread.stop()
        thread.join()
        thread=None

    syscalls="execve,open,socket,connect,accept,sendto,recvfrom,sendmsg,recvmsg,bind,listen,socketpair,accept4,recvmmsg,sendmmsg"
    thread = StraceProcess(" ".join(sys.argv[1:]), syscalls, callback)
    print "Quit with CTRL+C"

    signal.signal(signal.SIGINT, signal_handler)
    thread.start()

    while thread:
       time.sleep(1)


