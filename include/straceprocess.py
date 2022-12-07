#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import subprocess
from threading import Thread

class StraceProcess(Thread):
    def __init__(self, pid=None, program=None, syscalls="", callback=None):
        Thread.__init__(self)
        self.pid=pid
        self.program=program
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
            args=None
            if self.pid!=None:
                args=["strace", "-f", "-q", "-p", self.pid, "-e", self.syscalls, "-y" ]
            elif self.program!=None:
                args=["strace", "-f", "-q", "-e", self.syscalls, "-y"]
                if type(self.program)==list:
                    args.extend(self.program)
                else:
                    args.append(self.program)

            else:
                print ("PID or program is required !")
                return

            self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.running=True
            for line in iter(self.process.stdout.readline, b''):
                self.stdout(line.decode().replace('\n', ''))
                if self.process==None :
                    break

        except OSError:
            print ("Failed to use strace.")

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
        print (msg)

    syscalls="execve,open,openat,rename,socket,connect,accept,sendto,recvfrom,sendmsg,recvmsg,bind,listen,socketpair,accept4,recvmmsg,sendmmsg"
    thread = StraceProcess(program="/usr/sbin/arp", syscalls=syscalls, callback=callback)
    thread.start()
    thread.join()



