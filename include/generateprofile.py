#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re

class GenerateProfile():
    def __init__(self, allowedSyscallDic):
        self.allowedSyscallDic=allowedSyscallDic
        self.alreadyparse=False
        self.profileString=""

    def removeRegEx(self, line):
        line=re.sub(r'(\^|\$)', '',line)
        line=line.replace("\\.",".").replace(".*","*")
        return line


    def addToprofileString(self, line):
        if self.profileString!="":
            self.profileString+="\n"
        self.profileString+=self.removeRegEx(line)
        
    def parse(self):
        self.alreadyparse=True
        for key in self.allowedSyscallDic.keys():
            value=self.allowedSyscallDic[key]
            if type(value)==list:
                for v in value:
                    item=[key]
                    item.extend(v)
                    self.addToprofileString(";".join(item))
            elif value==True:
                self.addToprofileString(key)


    def getPrfStrings(self):
        if not self.alreadyparse:
            self.parse()
        return self.profileString
        
    def writeToFilePrf(self, filename):
        l=self.getPrfStrings().split('\n')
        try:
            f = open(filename,"w")
            for line in l:
                f.write(line+'\n')
            f.close()
        except:
            print "Impossible to write to file {}".format(filename)
            return False
        return True
        

if __name__ == '__main__':
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
    prf=GenerateProfile(profile)
    print prf.getPrfStrings()
    prf.writeToFilePrf("/tmp/tmpprofile.prf")


