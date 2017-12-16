#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re
import regex
from threading import Lock

"""
Create rules automatically, from system calls.
Is able to optimize some rules.
"""

class GenRulesSysCalls():
    def __init__(self, profile, debug=False, loglevel=1):
        self.profile=profile
        self.newprofile={}
        self.cacheFullProfile=[]
        self.lock_cachefullprofile = Lock()
        self._debug=debug
        self.loglevel=loglevel
        self.importProfile()


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
                        item.append(regex.removeRegEx(c))
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
            if value not in currentvalue:
                currentvalue.append(value)
                self.newprofile[key]=currentvalue

    def removeDuplicatedRegex(self, l):
        """see optimizes"""
        def addToTodoRemove(rm):
            if rm not in todoRemove:
                todoRemove.append(rm)
        newoptimized=[]
        todoRemove=[]
        
        for item in l:
            if item in newoptimized:
                continue
            if len(item)==1:
                newoptimized.append(item)
            elif len(item)==2:
                found=False
                for v in newoptimized:
                    if len (v)!=2:
                        continue
                    if v[0]==item[0]:
                        a=regex.escapeRegEx(item[1])
                        b=regex.escapeRegEx(v[1])
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
                        a1=regex.escapeRegEx(item[1])
                        b1=regex.escapeRegEx(v[1])
                        a2=regex.escapeRegEx(item[2])
                        b2=regex.escapeRegEx(v[2])
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

        newoptimized=self.removeDuplicate(newoptimized)
        for c in todoRemove:
            if c in newoptimized:
                newoptimized.remove(c)
        
        return newoptimized

    def removeDuplicate(self, l):
        newlist=[]
        for i in l:
            if i not in newlist:
                newlist.append(i)
        return newlist
    
    def reducePathSize(self, l):
        for item in l:
            if item[0]=="open" and len(item)>2 and item[2]=="O_RDONLY":
                path=item[1].split("/")
                if len(path)>2 and (path[1]=='proc' or path[1]=='sys'or path[1]=='run'):
                    path[2]="*"
                    path="/".join(path[0:3])
                    item[1]=path
                elif len(path)>3:
                    path[3]="*"
                    path="/".join(path[0:4])
                    item[1]=path
                

        return self.removeDuplicate(l)
    
    def optimizes(self, l):
        self.debug("len before optimization : {}".format(len(l)), 4)
        tmpl=self.reducePathSize(l)
        self.debug("len after reducePathSize : {}".format(len(tmpl)), 4)
        tmpl=self.removeDuplicatedRegex(tmpl)
        self.debug("len after removeDuplicatedRegex : {}".format(len(tmpl)), 4)
        newoptimized=[]
        for item in tmpl:
            if len(item)==1:
                if item in newoptimized:
                    pass
                newoptimized.append(item)
            elif len(item)==2:
                itemexist=None
                if not '*' in item[1] and not '/' in item[1]:
                    for v in newoptimized:
                        if len(v)==2:
                            if v[0]==item[0]:
                                if len(v[1])<30:
                                    itemexist=v
                                    break
                if itemexist!=None and item[1] not in itemexist[1] and itemexist[1] not in item[1]:
                    newoptimized.remove(itemexist)
                    itemexist=[itemexist[0], itemexist[1]+"|"+item[1] ]
                    newoptimized.append(itemexist)
                else:
                    newoptimized.append(item)
            elif len(item)==3:
                itemexist=None
                if not '*' in item[2] and not '/' in item[2]:
                    for v in newoptimized:
                        if len(v)==3:
                            if v[0]==item[0] and v[1]==item[1]:
                                if len(v[2])<30:
                                    itemexist=v
                                    break
                if itemexist!=None and item[2] not in itemexist[2] and itemexist[2] not in item[2]:
                    newoptimized.remove(itemexist)
                    itemexist=[itemexist[0], itemexist[1], itemexist[2]+"|"+item[2] ]
                    newoptimized.append(itemexist)
                else:
                    newoptimized.append(item)     
        self.debug("len after optimization : {}".format(len(newoptimized)), 4)
        return newoptimized

    def exportProfile(self):
        tmpFullProfile=self.optimizes(self.cacheFullProfile)
        self.newprofile={}
        for item in tmpFullProfile:
            syscall=item[0]
            value=item[1:]
            if len(item)==1:
                self.createKeyIfnotExist(syscall, True)
            else:
                self.createKeyIfnotExist(syscall, [])
            value=[]
            for v in item[1:]:
                v=regex.escapeRegEx(v.strip())
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
        "open" : [['^/lib/.*$', '^O_RDONLY$']]
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
    genrules.addSyscall(['open', '/etc/ssh/ssh_host_ed25519_key.pub', 'O_RDWR'])
    genrules.addSyscall(['open', '/etc/ssl/certs/ca-certificates.crt', 'O_RDONLY'])
    genrules.addSyscall(['socket', 'SOCK_DGRAM'])
    genrules.addSyscall(['socket', 'SOCK_STREAM'])
    genrules.addSyscall(['open' , '/proc/4355/fd' , 'O_RDONLY'])

    print "========\nbefore :", profile
    res=genrules.getProfile()
    print "========\nafter  :", res



