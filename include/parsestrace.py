#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re, sys
#import straceprocess
import straceprocess_debug as straceprocess # TODO
from threading import Thread, Lock


class ParseStrace(Thread):
    def __init__(self, pid, profile, debug=False, loglevel=1):
        Thread.__init__(self)
        self.pid=pid
        self.syscallsDicPattern={
            "execve"     : ".*\(\"(.*)\",.*",
            "open"       : ".*\(\"(.*)\",.*(O_RDONLY|O_RDWR|O_WRONLY).*",
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
                elif value == False:
                    return False
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
                self.debug("Is Not allowed (not in dic) : {}".format(syscall),6)
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
                        print ">>> TODO FIXME", syscall, msg
                        return
                if not self.checkIsAllowed(key):
                    self.debug("It is not allowed : {}".format(key),4)
                else:
                    self.debug("It is allowed : {}".format(key),6)


    def isRunning(self):
        return self.straceprocessthread.isRunning()

    def run(self):
        self.debug("Starting strace ...", 0)
        if self.straceprocessthread :
            return
        syscalls=",".join(self.syscalls)
        self.straceprocessthread = straceprocess.StraceProcess(self.pid, syscalls, self.callback)
        self.straceprocessthread.start()
        self.debug("strace started", 0)

    def stop(self):
        self.debug("Stopping strace ...", 0)
        if self.straceprocessthread==None :
            return
        self.straceprocessthread.stop()
        self.straceprocessthread.join()
        self.straceprocessthread=None
        self.debug("strace stopped", 0)


if __name__ == '__main__':
    import signal, time
    global thread
    profile={
        "execve": True,
        "bind" : True,
        "sendto" : True,
        "connect" : True,
        "listen" : True,
        "recvfrom" : True,
        "socket": [["^SOCK_RAW|SOCK_STREAM|SOCK_DGRAM$"]],
        "open" : [['^/dev/null$', '^O_RDWR$'],['^\.$', '^O_RDONLY$'],['^/proc/.*$', '^O_RDONLY$'],['^/dev/.*$', '^O_RDONLY$'], ['^/lib/.*$', '^O_RDONLY$'], ['^/usr/.*$', '^O_RDONLY$'], ['^/etc/.*$', '^O_RDONLY|O_RDWR$']]
    }

    thread = ParseStrace(" ".join(sys.argv[1:]), profile, debug=True, loglevel=4)
    print "Quit with CTRL+C"

    def signal_handler(signal, frame):
        print "Wait. Stopping all ..."
        global thread
        thread.stop()
        thread.join()
        thread=None

    signal.signal(signal.SIGINT, signal_handler)
    thread.start()

    while thread:
       time.sleep(1)


