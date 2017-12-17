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
    def test_classParseProfileFileTest(self):
        profile={
            "execve": [['^/bin/ls$'], ['^/bin/cat$']],
            "bind" : True,
            "sendto" : True,
            "connect" : True,
            "listen" : True,
            "recvfrom" : True,
            "socket": [["^SOCK_RAW|SOCK_STREAM|SOCK_DGRAM$"]],
            "open" : [['^/dev/null$', '^O_RDWR$'],['^\.$', '^O_RDONLY$'],['^/proc/.*$', '^O_RDONLY$'],['^/dev/.*$', '^O_RDONLY$'], ['^/lib/.*$', '^O_RDONLY$'], ['^/usr/.*$', '^O_RDONLY$'], ['^/etc/.*$', '^O_RDONLY|O_RDWR$']]
        }
        prf=ParseProfileFile("utest/sshd.prf")
        self.assertEqual(profile,prf.getDic())
        prf=ParseProfileFile("utest/sshd2.prf")
        self.assertEqual({'execve': True},prf.getDic())

    def test_createKeyIfnotExist(self):
        prf=ParseProfileFile("")
        prf.createKeyIfnotExist("key","value")
        self.assertEqual({'key': 'value'},prf.dic)
        prf.createKeyIfnotExist("key","value")
        self.assertEqual({'key': 'value'},prf.dic)
        prf.createKeyIfnotExist("key2","value")
        self.assertEqual({'key': 'value', 'key2': 'value'},prf.dic)

    def test_addtoDic(self):
        prf=ParseProfileFile("")
        prf.createKeyIfnotExist("key",True)
        prf.addtoDic("key",["value"]) # must not do anything
        self.assertEqual({'key': True},prf.dic)
        prf.createKeyIfnotExist("key2",[])
        prf.addtoDic("key2",["value1", "value2"])
        self.assertEqual({'key': True, 'key2': [['value1', 'value2']]},prf.dic)
        prf.createKeyIfnotExist("key3",[])
        prf.addtoDic("key3",["value1", "value2"])
        self.assertEqual({'key': True, 'key2': [['value1', 'value2']], 'key3': [['value1', 'value2']]},prf.dic)



class GenRulesSysCallsTest(unittest.TestCase):
    def setUp(self):
        self.profile={
            "execve": True,
            "sendto" : True,
            "connect" : True,
            "listen" : True,
            "open" : [['^/lib/.*$', '^O_RDONLY$']]
        }

    def test_classGenRulesSysCalls(self):
        genrules = GenRulesSysCalls(self.profile)
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['listen'])
        self.profile['listen']=True
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['execve', '/bin/ls'])
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['recvfrom'])
        self.profile['recvfrom']=True
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['open', '/lib/1/TODOREMOVE','O_RDONLY'])
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['open', '/lib/1/NOTREMOVE','O_RDWR'])
        self.profile["open"]=[['^/lib/.*$', '^O_RDONLY$'], ['^/lib/1/NOTREMOVE$', '^O_RDWR$']]
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['socket', 'SOCK_DGRAM'])
        self.profile["socket"]=[['^SOCK_DGRAM$']]
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['socket', 'SOCK_STREAM'])
        self.profile["socket"]=[['^SOCK_DGRAM|SOCK_STREAM$']]
        self.assertEqual(self.profile, genrules.getProfile())
        genrules.addSyscall(['open', '/etc/passwd', 'O_RDONLY'])
        self.profile["open"]=[['^/lib/.*$', '^O_RDONLY$'], ['^/lib/1/NOTREMOVE$', '^O_RDWR$'], ['^/etc/passwd$', '^O_RDONLY$']]
        self.assertEqual(self.profile, genrules.getProfile())

    def test_addToCacheIfnotExist(self):
        genrules = GenRulesSysCalls({})
        genrules.addToCacheIfnotExist("test")
        self.assertEqual(['test'], genrules.cacheFullProfile)
        genrules.addToCacheIfnotExist("test")
        self.assertEqual(['test'], genrules.cacheFullProfile)
        genrules.addToCacheIfnotExist("test2")
        self.assertEqual(['test', 'test2'], genrules.cacheFullProfile)


    def test_importProfile(self):
        genrules = GenRulesSysCalls(self.profile)
        self.assertEqual([['listen'], ['open', '/lib/*', 'O_RDONLY'], ['connect'], ['execve'], ['sendto']], genrules.cacheFullProfile)

    def test_createKeyIfnotExist(self):
        genrules = GenRulesSysCalls({})
        self.assertEqual({}, genrules.newprofile)
        genrules.createKeyIfnotExist("key", "value")
        self.assertEqual({'key': 'value'}, genrules.newprofile)
        genrules.createKeyIfnotExist("key", "value2") # must not do anything
        self.assertEqual({'key': 'value'}, genrules.newprofile)

    def test_addtoDic(self):
        genrules = GenRulesSysCalls({})
        genrules.createKeyIfnotExist("key",True)
        genrules.addtoDic("key",["value"]) # must not do anything
        self.assertEqual({'key': True},genrules.newprofile)
        genrules.createKeyIfnotExist("key2",[])
        genrules.addtoDic("key2",["value1", "value2"])
        self.assertEqual({'key': True, 'key2': [['value1', 'value2']]},genrules.newprofile)
        genrules.createKeyIfnotExist("key3",[])
        genrules.addtoDic("key3",["value1", "value2"])
        self.assertEqual({'key': True, 'key2': [['value1', 'value2']], 'key3': [['value1', 'value2']]},genrules.newprofile)

    def test_removeDuplicatedRegex(self):
        genrules = GenRulesSysCalls({})
        l=[['listen'], ['open', '/lib/*', 'O_RDONLY']]
        self.assertEqual(l, genrules.removeDuplicatedRegex(l))
        l2=l[:]
        l2.append(['open', '/lib/TODOREMOVE', 'O_RDONLY'])
        self.assertEqual(l, genrules.removeDuplicatedRegex(l2))
        l2=l[:]
        l2.append(['open', '/lib/NOTREMOVE', 'O_RDWR'])
        self.assertEqual(l2, genrules.removeDuplicatedRegex(l2))
        l2=l[:]
        l2.append(['open', '/lib/*', '*'])
        self.assertEqual([['listen'], ['open', '/lib/*', '*']], genrules.removeDuplicatedRegex(l2))
        l2.append(['open', '/lib/*', '*'])
        self.assertEqual([['listen'], ['open', '/lib/*', '*']], genrules.removeDuplicatedRegex(l2))
        l2.append(['open', '*', '*'])
        self.assertEqual([['listen'], ['open', '*', '*']], genrules.removeDuplicatedRegex(l2))

    def test_removeDuplicate(self):
        genrules = GenRulesSysCalls({})
        l=[1,1,1,1,2,2,2,2,3,3,4,4,1]
        self.assertEqual([1, 2, 3, 4], genrules.removeDuplicate(l))

    def test_reducePathSize(self):
        genrules = GenRulesSysCalls({})
        l=[['listen'], ['open', '/lib/1/2/3/4', 'O_RDONLY']]
        self.assertEqual([['listen'], ['open', '/lib/1/*', 'O_RDONLY']], genrules.reducePathSize(l))
        l=[['listen'], ['open', '/lib/1/2/3/4', 'O_RDONLY'], ['open', '/lib/5/6/7/8', 'O_RDONLY']]
        self.assertEqual([['listen'], ['open', '/lib/1/*', 'O_RDONLY'], ['open', '/lib/5/*', 'O_RDONLY']], genrules.reducePathSize(l))
        l=[['listen'], ['open', '/lib/1/DONOTREMOVE', 'O_RDWR']]
        self.assertEqual([['listen'], ['open', '/lib/1/DONOTREMOVE', 'O_RDWR']], genrules.reducePathSize(l))
        l=[['listen'], ['open' , '/proc/4355/fd' , 'O_RDONLY'], ['open' , '/sys/test' , 'O_RDONLY'], ['open' , '/run/test' , 'O_RDONLY']]
        self.assertEqual([['listen'], ['open', '/proc/*', 'O_RDONLY'], ['open', '/sys/*', 'O_RDONLY'], ['open', '/run/*', 'O_RDONLY']], genrules.reducePathSize(l))

    def test_optimizes(self):
        genrules = GenRulesSysCalls({})
        l=[['listen'], ['listen'], ['listen']]
        self.assertEqual([['listen']], genrules.optimizes(l))
        l=[['listen'], ['recvfrom'], ['connect']]
        self.assertEqual([['listen'], ['recvfrom'], ['connect']], genrules.optimizes(l))
        l=[['execve', '/bin/ls']]
        self.assertEqual( [['execve', '/bin/ls']], genrules.optimizes(l))
        l=[['execve', '/bin/ls'], ['execve', '/bin/cat']]
        self.assertEqual( [['execve', '/bin/ls'], ['execve', '/bin/cat']], genrules.optimizes(l))
        l=[['execve', 'ls'], ['execve', 'cat']]
        self.assertEqual( [['execve', 'ls|cat']], genrules.optimizes(l))
        l=[['execve', 'ls*'], ['execve', 'cat*']]
        self.assertEqual( [['execve', 'ls*'], ['execve', 'cat*']], genrules.optimizes(l))
        l=[['socket', 'SOCK_DGRAM'], ['socket', 'SOCK_STREAM']]
        self.assertEqual([['socket', 'SOCK_DGRAM|SOCK_STREAM']], genrules.optimizes(l))
        l=[['open', '/etc/passwd', 'O_RDONLY'], ['open', '/etc/passwd', 'O_RDONLY']]
        self.assertEqual([['open', '/etc/passwd', 'O_RDONLY']], genrules.optimizes(l))
        l=[['open', '/etc/passwd', 'O_RDONLY'], ['open', '/etc/passwd', 'O_RDWR']]
        self.assertEqual([['open', '/etc/passwd', 'O_RDONLY|O_RDWR']], genrules.optimizes(l))
        l=[['open', '/etc/shadow', 'O_RDONLY'], ['open', '/etc/passwd', 'O_RDWR']]
        self.assertEqual([['open', '/etc/shadow', 'O_RDONLY'], ['open', '/etc/passwd', 'O_RDWR']], genrules.optimizes(l))


if __name__ == '__main__':
    unittest.main()



