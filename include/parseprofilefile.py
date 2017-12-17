#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017


import re
import regex

"""
Get rules, from file.
"""

class ParseProfileFile():
    def __init__(self, filename):
        self.filename=filename
        self.dic={}
        self.alreadyread=False

    def createKeyIfnotExist(self, key, value):
        if not key in self.dic:
            self.dic[key]=value

    def addtoDic(self, key, value):
        currentvalue=self.dic[key]
        if currentvalue==True:
            return
        elif type(currentvalue)==list and type(value)==list and len(value)!=0:
            if value not in currentvalue:
                currentvalue.append(value)
                self.dic[key]=currentvalue

    def parse(self):
        self.alreadyread=True
        try:
            with open(self.filename) as f:
                for line in f.readlines():
                    line=line.replace('\n', '').strip()
                    if line=="":
                        continue

                    l=line.split(";")
                    key=l[0].strip()
                    if len(l)==1:
                        self.dic[key]= True
                    else:
                        self.createKeyIfnotExist(key, [])

                        value=[]
                        for v in l[1:]:
                            v=regex.escapeRegEx(v.strip())
                            value.append(v)
                        self.addtoDic(key, value)
        except IOError:
            print "Impossible to read profile file !"
            return False
        return True

    def getDic(self):
        if not self.alreadyread:
            if not self.parse():
                self.dic=None
        return self.dic



if __name__ == '__main__':
    prf=ParseProfileFile("../profiles/sshd.prf")
    print prf.getDic()


