#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re
from threading import Thread, Lock


class GenRulesSysCalls(Thread):
    def __init__(self, profile, debug=False, loglevel=1):
        Thread.__init__(self)
        self.profile=profile
        self.newprofile={}
        self.cacheFullProfile=[]
        self.lock_cachefullprofile = Lock()
        self.running=False
        self._debug=debug
        self.loglevel=loglevel
        self.importProfile()
        print "FIN ============================" # TODO

    def removeRegEx(self, line):
        line=re.sub(r'(\^|\$)', '',line)
        line=line.replace("\\.",".").replace(".*","*")
        return line

    def escapeRegEx(self, line):
        line=line.replace('.', '\\.').replace('*', '.*')
        line="^"+line+"$"
        return line



    def addToCacheIfnotExist(self, value):
        if value not in self.cacheFullProfile:
            self.debug("Add to cache: {}".format(value), 7)
            self.lock_cachefullprofile.acquire()
            self.cacheFullProfile.append(value)
            self.lock_cachefullprofile.release()


    def importProfile(self):
        """convert entries from dictionay to list"""
        for key in self.profile.keys():
            value=self.profile[key]
            if type(value)==list:
                for v in value:
                    item=[key]
                    for c in v:
                        item.append(self.removeRegEx(c))
                    self.addToCacheIfnotExist(item)
            elif value==True:
                self.addToCacheIfnotExist([key])


    def createKeyIfnotExist(self, key, value):
        """see optimizes"""
        if not key in self.newprofile:
            self.newprofile[key]=value

    def addtoDic(self, key, value):
        """see optimizes"""
        currentvalue=self.newprofile[key]
        if currentvalue==True:
            return
        elif type(currentvalue)==list and type(value)==list and len(value)!=0:   
            currentvalue.append(value)
            self.newprofile[key]=currentvalue

     
    def optimizes(self, l):
        tmpl=l[:]
        newoptimized=[]
        print "==========================="
        print "len before ", len(tmpl)
        for item in l:
            if len(item)==1:
                if item in newoptimized:
                    pass
                newoptimized.append(item)
            if len(item)==2:
                found=False
                itemexist=None
                for v in newoptimized:
                    if len(v)==2:
                        if v[0]==item[0]:
                            if len(v[1])<30:
                                found=True
                                itemexist=v
                            break
                if found==True:
                    newoptimized.remove(v)
                    v=[v[0], v[1]+"|"+item[1] ]
                    newoptimized.append(v)
                else:
                    newoptimized.append(item)
            if len(item)==3:
                found=False
                itemexist=None
                for v in newoptimized:
                    if len(v)==3:
                        if v[0]==item[0] and v[1]==item[1]:
                            if len(v[2])<30:
                                found=True
                                itemexist=v
                            break
                if found==True:
                    newoptimized.remove(v)
                    v=[v[0], v[1], v[2]+"|"+item[2] ]
                    newoptimized.append(v)
                else:
                    newoptimized.append(item)     
                        
        print "len after ", len(newoptimized)
        print "==========================="
        return newoptimized 

    def exportProfile(self):
        tmpFullProfile=self.optimizes(self.cacheFullProfile)
        
        for item in tmpFullProfile:
            syscall=item[0]
            value=item[1:]
            if len(item)==1:
                self.createKeyIfnotExist(syscall, True)
            else:
                self.createKeyIfnotExist(syscall, [])
            value=[]
            for v in item[1:]:
                v=self.escapeRegEx(v.strip())
                value.append(v)
            self.addtoDic(syscall, value)
                

    def debug(self, msg, level=1):
        if self._debug and level<=self.loglevel:
            print(msg)

    def run(self):
        self.running=True

    def addSyscall(self, l):
        self.addToCacheIfnotExist(l)


    def getProfile(self):
        self.exportProfile()
        return self.newprofile

    def isRunning(self):
        return self.running

    def stop(self):
        self.running=False


if __name__ == '__main__':
    import signal, time
    global thread
    profile={
        "execve": True,
        "sendto" : True,
        "connect" : True,
        "listen" : True,
        "open" : [['^/lib/.*$', '^O_RDONLY$'],['^/etc/.*$', '^O_RDONLY$']]
    }

    thread = GenRulesSysCalls(profile, debug=True, loglevel=7)
    print "Quit with CTRL+C"

    def signal_handler(signal, frame):
        print "Wait. Stopping all ..."
        global thread
        print "before :", profile
        print "after  :", thread.getProfile()
        thread.stop()
        thread.join()
        thread=None

    signal.signal(signal.SIGINT, signal_handler)
    thread.start()
    
    thread.addSyscall(['listen'])
    thread.addSyscall(['execve', '/bin/ls'])
    thread.addSyscall(['recvfrom'])
    thread.addSyscall(['open', '/etc/ld.so.cache', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ld.so.cache', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ld.so.cache', 'O_RDWR'])
    thread.addSyscall(['open', '/etc/ssh/sshd_config', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/gai.conf', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/nsswitch.conf', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/passwd', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_rsa_key', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_rsa_key.pub', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_dsa_key', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_dsa_key.pub', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_ecdsa_key', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_ecdsa_key.pub', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_ed25519_key', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssh/ssh_host_ed25519_key.pub', 'O_RDONLY'])
    thread.addSyscall(['open', '/etc/ssl/certs/ca-certificates.crt', 'O_RDONLY'])
    thread.addSyscall(['socket', 'SOCK_DGRAM'])
    thread.addSyscall(['socket', 'SOCK_STREAM'])

    while thread:
       time.sleep(1)


