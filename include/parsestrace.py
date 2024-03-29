#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re
try:
    import straceprocess
except:
    import include.straceprocess as straceprocess

from threading import Thread, Lock


class ParseStrace(Thread):
    def __init__(self, pid=None, program=None, profile={}, callbackWarning=None, debug=False, loglevel=1):
        Thread.__init__(self)
        self.pid=pid
        self.program=program
        self.callbackWarning=callbackWarning
        self.syscallsDicPattern={
            "execve"     : ".*\(\"(\S+)\",.*",
            "open"       : ".*\(\"(\S+)\",.*(O_RDONLY|O_RDWR|O_WRONLY).*",
            "openat"     : ".*\(AT_.*,\s*\"(\S+)\",.*(O_RDONLY|O_RDWR|O_WRONLY).*",
            "rename"     : ".*\(\"(\S+)\",\s*\"(\S+)\"",
            "socket"     : ".*(SOCK_DGRAM|SOCK_RAW|SOCK_STREAM|SOCK_SEQPACKET).*",
            "connect"    : None,
            "accept"     : None,
            "sendto"     : None,
            "recvfrom"   : None,
            "sendmsg"    : ".*family=AF_INET.*",
            "recvmsg"    : ".*family=AF_INET.*",
            "bind"       : ".*family=AF_INET.*",
            "listen"     : None,
            "socketpair" : None,
            "accept4"    : None,
            "sendmmsg"   : None
        }
        self.syscalls=self.syscallsDicPattern.keys()
        self.straceprocessthread=None
        self._debug=debug
        self.loglevel=loglevel
        self.cachesyscalls=[]
        self.lock_cachesyscalls = Lock()
        self.allowedSyscallDic=profile
        self.debug(profile,3)

    def debug(self, msg, level=1):
        if self._debug and level<=self.loglevel:
            print(msg)


    def addInCache(self, key):
        self.lock_cachesyscalls.acquire()
        self.cachesyscalls.append(key)
        self.lock_cachesyscalls.release()

    def isInCache(self, key):
        if key in self.cachesyscalls:
            return True
        else:
            return False

    def checkIsAllowed(self, key):
        if self.isInCache(key):
            return True
        else:
            # first add it
            self.addInCache(key)
            syscall=key[0]
            if syscall in self.allowedSyscallDic:
                value=self.allowedSyscallDic[syscall]
                if value == True:
                    return True
                elif type(value) == list:
                    toCheck=key[1:]
                    for it in value:
                        match=0
                        for v in it:
                            for c in toCheck:
                                m = re.match( r'{}'.format(v), c)
                                if m!=None:
                                    match+=1
                        if len(it)==match:
                            # all patterns matches !
                            self.debug("All pattern matches. {} - {} ".format(key, it),6)
                            return True

                else:
                    self.debug("Unknown Error :  {}".format(value),6)
            else:
                self.debug("Not allowed (not in dic) : {}".format(syscall),6)
        if self.callbackWarning:
            self.callbackWarning(key)
        return False

    def callback(self, msg):
        self.debug(msg, 8)
        matchObj = re.match( r'^(\[pid\s+\d+\]\s+){0,1}(\S+)\(', msg)
        if matchObj:
            syscall=matchObj.group(2)
            if syscall in self.syscalls:
                # default value
                key=[syscall]
                pattern=self.syscallsDicPattern[syscall]
                if pattern!=None:
                    m = re.match( r'{}'.format(pattern), msg)
                    if m!=None:
                        key.extend(m.groups())
                    else:
                        self.debug("syscall exist in dictionary but pattern not match: syscall:{}, pattern:'{}', strace:{} ...".format(syscall, pattern, msg[0:50]),6)
                        return
                if not self.checkIsAllowed(key):
                    self.debug("Not allowed : {}".format(key),4)


    def isRunning(self):
        if self.straceprocessthread:
            return self.straceprocessthread.isRunning()
        return False


    def run(self):
        self.debug("Starting strace ...", 0)
        if self.straceprocessthread :
            return
        syscalls=",".join(self.syscalls)
        self.straceprocessthread = straceprocess.StraceProcess(self.pid, self.program, syscalls, self.callback)
        self.straceprocessthread.start()
        self.debug("strace started", 0)
        self.straceprocessthread.join()
        self.straceprocessthread=None
        self.debug("strace stopped", 0)

    def stop(self):
        if self.straceprocessthread==None :
            return
        self.debug("Stopping strace ...", 0)
        self.straceprocessthread.stop()


if __name__ == '__main__':
    profile={
        "execve": True
    }

    def callbackWarning(l):
        print ("not allowed : ", l)

    thread = ParseStrace(program="/usr/sbin/arp", profile=profile, callbackWarning=callbackWarning, debug=True, loglevel=4)
    thread.start()
    thread.join()


