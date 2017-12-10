#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Written by Daniel Rocher <erable@resydev.fr>
# Portions created by the Initial Developer are Copyright (C) 2016


__version__="0.4"


import argparse
import sys, time, signal, psutil, os

from include.parsestrace import *
from include.parseprofilefile import *
from include.genrulessyscalls import *
from include.generateprofile import *

class Main():
    def __init__(self):
        self.debug=False
        self.argparse_thread=None
        self.profile=False
        self.genrules=False
        self.genrules_filename=""
        self.leveldebug=0
        self.pid=None
        self.program=None

        # parse arguments
        self.parseArgs()

        # SIGINT for interrupt program
        signal.signal(signal.SIGINT, self.signal_handler)

        dic={}
        if self.profile!=False:
            prf=ParseProfileFile(self.profile)
            dic=prf.getDic()
            if dic==None:
                sys.exit(1)

        self.genProf=None
        if self.genrules:
            self.genProf=GenRulesSysCalls(dic, debug=self.debug, loglevel=self.leveldebug)

        self.argparse_thread=ParseStrace(self.pid, self.program, dic, callbackWarning=self.callbackWarning, debug=self.debug, loglevel=self.leveldebug) # TODO Fixme
        self.argparse_thread.start()
        
        while self.argparse_thread:
            time.sleep(1)

    def callbackWarning(self, l):
        print "New call : {}".format(l)
        if self.genrules:
            self.genProf.addSyscall(l)


    def signal_handler(self, signal, frame):
        self.printDebug("Wait. Stopping all ...")
        self.argparse_thread.stop()
        self.argparse_thread.join()
        if self.genrules:
            # write new profile in file
            dic=self.genProf.getProfile()
            prf=GenerateProfile(dic)
            prf.writeToFilePrf(self.genrules_filename)
        self.argparse_thread=None

    def printDebug(self, msg):
        if self.debug:
            print(str(msg))

    def parseArgs(self):
        # Parse Args
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--version", help="show version", action="store_true")
        parser.add_argument("-p", "--profile", help="profile file", metavar="PROFIL_FILENAME")
        parser.add_argument("-o", "--ouput", help="generate new profile with rules", metavar="OUTPUT_FILENAME")
        parser.add_argument("-d", "--debug", help="Debug", action="store_true")
        parser.add_argument("-l", "--leveldebug", help="level for debug",type=int, default=0)
        parser.add_argument("TRACE", help="A Pid number (ex. 545) OR PidName (ex. sshd) OR start program to trace (ex. /usr/sbin/sshd). Pid and PidName must be running")
        args=parser.parse_args()

        if (not args.debug and args.leveldebug!=0):
            parser.error('--leveldebug (-l) require --debug (-d) !')


        appName=sys.argv[0]
        if args.version==True:
            print ("{0} version : {1}".format(appName, __version__))
            sys.exit()
        if args.debug==True:
            self.debug=True
            self.leveldebug=args.leveldebug

        if args.profile:
            self.profile=args.profile

        if args.ouput:
            self.genrules_filename=args.ouput  
            self.genrules=True 

        # test if a number
        try:
            pid_int=int(args.TRACE)
            self.pid=args.TRACE
            # test if pid running
            if not psutil.pid_exists(pid_int):
                print "PID {} not running !".format(self.pid)
                sys.exit(1)
        except ValueError:
            # search by name
            lPid=[]
            for proc in psutil.process_iter():
                if proc.name()==args.TRACE:
                    lPid.append(str(proc.pid))
            
            if len(lPid)>0:
                self.pid=",".join(lPid)
            else:
                pid=None
                # test if program exist
                if not os.path.isfile(args.TRACE):
                    print "File {} doesn't exist !".format(args.TRACE)
                    sys.exit(1)
                # test if file is executable
                if not os.access(args.TRACE, os.X_OK):
                    print "File {} is not executable !".format(args.TRACE)
                    sys.exit(1)
                self.program=args.TRACE

        if self.pid==None and self.program==None:
            print "PID or program is required !"
            sys.exit(1)   

if __name__ == "__main__":
    Main()



