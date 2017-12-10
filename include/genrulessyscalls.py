#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re
from threading import Lock


class GenRulesSysCalls():
    def __init__(self, profile, debug=False, loglevel=1):
        self.profile=profile
        self.newprofile={}
        self.cacheFullProfile=[]
        self.lock_cachefullprofile = Lock()
        self.running=False
        self._debug=debug
        self.loglevel=loglevel
        self.importProfile()

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

    def removeDuplicatedRegex(self, l):
        """see optimizes"""
        def addToTodoRemove(l):
            if l not in todoRemove:
                todoRemove.append(l)
        tmpl=l[:]
        newoptimized=[]
        todoRemove=[]
        
        for item in tmpl:
            if len(item)==1:
                newoptimized.append(item)
            elif len(item)==2:
                found=False
                for v in newoptimized:
                    if len (v)!=2:
                        continue
                    if v[0]==item[0]:
                        a=self.escapeRegEx(item[1])
                        b=self.escapeRegEx(v[1])
                        if re.match(r'{}'.format(a), '{}'.format(v[1])):
                            self.debug("{} - '{}' can replace '{}'".format(item[0], a, b),5)
                            addToTodoRemove(v)
                            continue
                        if re.match(r'{}'.format(b), '{}'.format(item[1])):
                            self.debug("{} - '{}' can replace '{}'".format(item[0], b, a),5)
                            addToTodoRemove(item)
                            continue
                if found==False:
                    newoptimized.append(item)
            elif len(item)==3:
                found=False
                for v in newoptimized:
                    if len (v)!=3:
                        continue
                    if v[0]==item[0]:
                        a1=self.escapeRegEx(item[1])
                        b1=self.escapeRegEx(v[1])
                        a2=self.escapeRegEx(item[2])
                        b2=self.escapeRegEx(v[2])
                        if re.match(r'{}'.format(a1), '{}'.format(v[1])) and re.match(r'{}'.format(a2), '{}'.format(v[2])) :
                            self.debug("{} - '{},{}' can replace '{},{}'".format(item[0], a1, a2, v[1], v[2]),5)
                            addToTodoRemove(v)
                            continue
                        if re.match(r'{}'.format(b1), '{}'.format(item[1])) and re.match(r'{}'.format(b2), '{}'.format(item[2])) :
                            self.debug("{} - '{},{}' can replace '{},{}'".format(item[0], b1, b2, item[1], item[2]),5)
                            addToTodoRemove(item)
                            continue
                if found==False:
                    newoptimized.append(item)

        for c in todoRemove:
            if c in newoptimized:
                newoptimized.remove(c)
        
        return newoptimized

    def optimizes(self, l):
        self.debug("len before optimization : {}".format(len(l)), 4)
        tmpl=self.removeDuplicatedRegex(l[:])
        self.debug("len after removeDuplicatedRegex : {}".format(len(tmpl)), 4)
        newoptimized=[]
        for item in tmpl:
            if len(item)==1:
                if item in newoptimized:
                    pass
                newoptimized.append(item)
            elif len(item)==2:
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
            elif len(item)==3:
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
        self.debug("len after optimization : {}".format(len(newoptimized)), 4)
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

    def addSyscall(self, l):
        self.addToCacheIfnotExist(l)


    def getProfile(self):
        self.exportProfile()
        return self.newprofile


if __name__ == '__main__':
    profile={
        "execve": True,
        "sendto" : True,
        "connect" : True,
        "listen" : True,
        "open" : [['^/lib/.*$', '^O_RDONLY$'],['^/etc/.*$', '^O_RDONLY$']]
    }

    genrules = GenRulesSysCalls(profile, debug=True, loglevel=5)
    genrules.addSyscall(['listen'])
    genrules.addSyscall(['execve', '/bin/ls'])
    genrules.addSyscall(['recvfrom'])
    genrules.addSyscall(['open', '/etc/ld.so.cache', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ld.so.cache', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ld.so.cache', 'O_RDWR'])
    genrules.addSyscall(['open', '/etc/ssh/sshd_config', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/gai.conf', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/nsswitch.conf', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/passwd', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_rsa_key', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_rsa_key.pub', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_dsa_key', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_dsa_key.pub', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_ecdsa_key', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_ecdsa_key.pub', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_ed25519_key', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_ed25519_key.pub', 'O_RDONLY'])
    genrules.addSyscall(['open', '/etc/ssl/certs/ca-certificates.crt', 'O_RDONLY'])
    genrules.addSyscall(['socket', 'SOCK_DGRAM'])
    genrules.addSyscall(['socket', 'SOCK_STREAM'])

    print "========\nbefore :", profile
    res=genrules.getProfile()
    print "========\nafter  :", res



