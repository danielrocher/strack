#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2017

import unittest
import include.regex as regex
import include.parsestrace as parsestrace
import utest.straceprocess_utest as straceprocess
from include.parseprofilefile import *
from include.genrulessyscalls import *
from include.generateprofile import *



class RegexTest(unittest.TestCase):
    def test_escapeRegEx(self):
        self.assertEqual('^$', regex.escapeRegEx(""))
        self.assertEqual('^\\.$', regex.escapeRegEx("."))
        self.assertEqual('^.*$', regex.escapeRegEx("*"))
        self.assertEqual('^\\..*\\.\\..*.*$', regex.escapeRegEx(".*..**"))

    def test_removeRegEx(self):
        self.assertEqual('', regex.removeRegEx(""))
        self.assertEqual('', regex.removeRegEx("^$"))
        self.assertEqual('.', regex.removeRegEx("^\\.$"))
        self.assertEqual('*', regex.removeRegEx("^.*$"))
        self.assertEqual('.*..**', regex.removeRegEx("^\\..*\\.\\..*.*$"))




class ParseStraceTest(unittest.TestCase):
    def setUp(self):
        self.thread=None
        self.required=[
            ['open', '/etc/ld.so.cache', 'O_RDONLY'], 
            ['open', '/etc/ld.so.cache', 'O_RDWR'],
            ['execve', './fork_exec'],
            ['bind'],
            ['socket', 'SOCK_STREAM'],
            ['connect']]

            
    def callbackWarning(self, l):
        self.syscall.append(l)

    def checkCache(self):
        # check if in cache
        self.assertEqual(len(self.required), len(self.thread.cachesyscalls))
        for c in self.required:
            self.assertTrue(c in self.thread.cachesyscalls)

    def test_capturedSyscall(self):
        self.profile={
            "execve": True,
            "bind" : True,
            "sendto" : True,
            "connect" : True,
            "listen" : True,
            "recvfrom" : True,
            "socket": [["^SOCK_RAW|SOCK_STREAM|SOCK_DGRAM$"]],
            "open" : [['^/dev/null$', '^O_RDWR$'],['^\.$', '^O_RDONLY$'],['^/proc/.*$', '^O_RDONLY$'],['^/dev/.*$', '^O_RDONLY$'], ['^/lib/.*$', '^O_RDONLY$'], ['^/usr/.*$', '^O_RDONLY$'], ['^/etc/.*$', '^O_RDONLY|O_RDWR$']]
        }
        self.syscall=[]
        self.thread = parsestrace.ParseStrace(program="utest/test_strace1.txt", profile=self.profile, callbackWarning=self.callbackWarning)
        parsestrace.straceprocess=straceprocess
        self.thread.start()
        self.thread.join()
        self.checkCache()
        # test if no unallowed
        self.assertEqual(0, len(self.syscall))
        
    def test_UnallowedSyscall(self):
        self.profile={
        }
        self.syscall=[]
        self.thread = parsestrace.ParseStrace(program="utest/test_strace1.txt", profile=self.profile, callbackWarning=self.callbackWarning)
        parsestrace.straceprocess=straceprocess
        self.thread.start()
        self.thread.join()
        self.checkCache()
        # test if unallowed
        self.assertEqual(6, len(self.syscall))
        for c in self.required:
            self.assertTrue(c in self.syscall)




class GenerateProfileTest(unittest.TestCase):
    def setUp(self):
        self.profile={
        "execve": True,
        "bind" : True,
        "sendto" : True,
        "connect" : True,
        "listen" : True,
        "recvfrom" : True,
        "socket": [["^SOCK_RAW|SOCK_STREAM|SOCK_DGRAM$"]],
        "open" : [['^/dev/null$', '^O_RDWR$'],['^\.$', '^O_RDONLY$'],['^/proc/.*$', '^O_RDONLY$']]
        }
        self.required=["recvfrom", "socket;SOCK_RAW|SOCK_STREAM|SOCK_DGRAM", "connect", "sendto", "bind","open;/dev/null;O_RDWR", "open;.;O_RDONLY",
            "open;/proc/*;O_RDONLY", "execve", "listen"]

    def test_addToprofileString(self):
        prf=GenerateProfile({})
        prf.addToprofileString("execve")
        self.assertEqual("execve", prf.profileString)
        prf.addToprofileString("bind")
        self.assertEqual("execve\nbind", prf.profileString)
        prf.addToprofileString("sendto")
        self.assertEqual("execve\nbind\nsendto", prf.profileString)

    def test_classGenerateProfile(self):
        prf=GenerateProfile(self.profile)
        prfStringsLst=prf.getPrfStrings().split('\n')
        self.assertEqual(len(self.required), len(prfStringsLst))
        for c in prfStringsLst:
            self.assertTrue(c in self.required)


class ParseProfileFileTest(unittest.TestCase):
    def setUp(self):
        pass

class GenRulesSysCallsTest(unittest.TestCase):
    def setUp(self):
        pass



if __name__ == '__main__':
    unittest.main()



